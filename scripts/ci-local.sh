#!/usr/bin/env bash
# =============================================================================
# Local CI Runner — mirrors the GitHub Actions pipeline
# =============================================================================
# Single idempotent entry point. Runs the same checks as CI, locally.
# Prompts for any missing environment variables when needed.
# Deploy steps are SKIPPED unless --deploy flag is passed.
# CrewAI review is SKIPPED unless --review flag is passed.
#
# Usage:
#   ./scripts/ci-local.sh              # Full CI (no deploy, no review)
#   ./scripts/ci-local.sh --review     # Full CI + CrewAI code review
#   ./scripts/ci-local.sh --deploy     # Full CI + deploy (requires CF creds)
#   ./scripts/ci-local.sh --step lint  # Run a single step
#
# Available steps: format, lint, lint-md, lint-css, typecheck, commitlint,
#                  link-check, test-crewai, test-website, build-website, review
#
# Environment:
#   Reads .env if present. Prompts interactively for missing vars when needed.
# =============================================================================

set -euo pipefail

# --- Configuration ---
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Flags
RUN_DEPLOY=false
RUN_REVIEW=false
RUN_FULL_REVIEW=false
REVIEW_LABELS=""
SINGLE_STEP=""
VERBOSE=false

# --- Colors & Symbols ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

PASS="✅"
FAIL="❌"
SKIP="⏭️ "
WARN="⚠️ "
RUNNING="🔄"
PHASE="═══"

# --- State Tracking ---
declare -A STEP_RESULTS
declare -A STEP_DURATIONS
TOTAL_START=$(date +%s)
STEPS_PASSED=0
STEPS_FAILED=0
STEPS_SKIPPED=0

# --- Load .env (if present) ---
if [[ -f "${REPO_ROOT}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${REPO_ROOT}/.env"
  set +a
fi

# --- Parse Args ---
while [[ $# -gt 0 ]]; do
  case $1 in
    --deploy)   RUN_DEPLOY=true; shift ;;
    --review)   RUN_REVIEW=true; shift ;;
    --full-review)
      RUN_REVIEW=true
      RUN_FULL_REVIEW=true
      shift ;;
    --crew)
      RUN_REVIEW=true
      REVIEW_LABELS="${REVIEW_LABELS:+$REVIEW_LABELS,}crewai:$2"
      shift 2 ;;
    --verbose)  VERBOSE=true; shift ;;
    --step)     SINGLE_STEP="$2"; shift 2 ;;
    --help|-h)
      echo "Usage: ./scripts/ci-local.sh [--review] [--full-review] [--crew <name>] [--deploy] [--step <name>] [--verbose]"
      echo ""
      echo "Flags:"
      echo "  --review        Run quick CrewAI code review (requires OPENROUTER_API_KEY)"
      echo "  --full-review   Run ALL 9 specialist crews (security, legal, finance, etc.)"
      echo "  --crew <name>   Run specific crew(s) — can be repeated (e.g. --crew security --crew legal)"
      echo "  --deploy        Run Cloudflare deploy (requires CF credentials)"
      echo "  --step <name>   Run a single step by name"
      echo "  --verbose       Show full command output"
      echo ""
      echo "Crews: security, legal, finance, docs, agentic, marketing, science, government, strategy"
      echo ""
      echo "Steps: format, lint, lint-md, lint-css, typecheck, commitlint,"
      echo "       link-check, test-crewai, test-website, build-website, review"
      echo ""
      echo "Examples:"
      echo "  ./scripts/ci-local.sh --review                   # Quick review only"
      echo "  ./scripts/ci-local.sh --full-review              # All 9 specialist crews"
      echo "  ./scripts/ci-local.sh --crew security --crew legal  # Specific crews"
      exit 0
      ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# =============================================================================
# Environment Validation & Interactive Prompts
# =============================================================================

prompt_env_var() {
  local var_name="$1"
  local description="$2"
  local is_secret="${3:-false}"

  if [[ -n "${!var_name:-}" ]]; then
    return 0
  fi

  echo ""
  echo -e "  ${YELLOW}${WARN}${NC} ${BOLD}${var_name}${NC} is not set."
  echo -e "  ${DIM}${description}${NC}"
  echo ""

  if [[ -t 0 ]]; then
    if [[ "$is_secret" == "true" ]]; then
      read -rsp "  Enter ${var_name} (hidden): " value
      echo ""
    else
      read -rp "  Enter ${var_name}: " value
    fi

    if [[ -n "$value" ]]; then
      export "${var_name}=${value}"
      echo -e "  ${PASS} ${var_name} set for this session."

      read -rp "  Save to .env for next time? [y/N] " save_answer
      if [[ "$save_answer" =~ ^[Yy] ]]; then
        echo "${var_name}=${value}" >> "${REPO_ROOT}/.env"
        echo -e "  ${PASS} Saved to .env"
      fi
      return 0
    fi
  fi

  return 1
}

check_env_for_review() {
  if ! prompt_env_var "OPENROUTER_API_KEY" \
    "Required for AI code review. Get one at https://openrouter.ai/keys" \
    "true"; then
    echo -e "  ${DIM}Skipping review — set OPENROUTER_API_KEY in .env or pass it interactively.${NC}"
    return 1
  fi
  return 0
}

check_env_for_deploy() {
  local ok=true
  if ! prompt_env_var "CLOUDFLARE_API_TOKEN" \
    "Required for Cloudflare Pages deploy. Create at https://dash.cloudflare.com/profile/api-tokens" \
    "true"; then
    ok=false
  fi
  if ! prompt_env_var "CLOUDFLARE_ACCOUNT_ID" \
    "Your Cloudflare Account ID. Found in the dashboard sidebar." \
    "false"; then
    ok=false
  fi
  $ok
}

# =============================================================================
# Dependency Check
# =============================================================================

check_dependencies() {
  local missing=()

  if ! command -v node &>/dev/null; then
    missing+=("node (install via nvm or https://nodejs.org)")
  fi
  if ! command -v pnpm &>/dev/null; then
    missing+=("pnpm (npm install -g pnpm)")
  fi
  if ! command -v python3 &>/dev/null && ! command -v python &>/dev/null; then
    missing+=("python3 (install via pyenv or https://python.org)")
  fi

  if [[ ${#missing[@]} -gt 0 ]]; then
    echo ""
    echo -e "  ${RED}${FAIL} Missing required tools:${NC}"
    for tool in "${missing[@]}"; do
      echo -e "     ${RED}•${NC} $tool"
    done
    echo ""
    exit 1
  fi

  # Install node deps if needed
  if [[ ! -d "${REPO_ROOT}/node_modules" ]]; then
    echo -e "  ${RUNNING} Installing Node dependencies..."
    (cd "${REPO_ROOT}" && pnpm install --frozen-lockfile 2>/dev/null || pnpm install 2>/dev/null)
    echo -e "  ${PASS} Dependencies installed."
  fi
}

# =============================================================================
# Idempotent Workspace Setup
# =============================================================================

clean_workspace() {
  local workspace_dir="${REPO_ROOT}/.crewai/workspace"
  if [[ -d "$workspace_dir" ]]; then
    rm -rf "$workspace_dir"
  fi
  mkdir -p "${workspace_dir}/trace"
}

# =============================================================================
# Helper Functions
# =============================================================================

print_header() {
  echo ""
  echo -e "${BLUE}${PHASE}${PHASE}${PHASE}${PHASE}${PHASE}${PHASE}${PHASE}${PHASE}${PHASE}${NC}"
  echo -e "${BOLD}${BLUE}  $1${NC}"
  echo -e "${BLUE}${PHASE}${PHASE}${PHASE}${PHASE}${PHASE}${PHASE}${PHASE}${PHASE}${PHASE}${NC}"
}

print_step() {
  echo -e "  ${RUNNING} ${BOLD}$1${NC} ${DIM}$2${NC}"
}

print_result() {
  local name="$1"
  local status="$2"
  local duration="$3"
  local detail="${4:-}"

  case "$status" in
    pass)
      echo -e "  ${PASS} ${GREEN}${name}${NC} ${DIM}(${duration}s)${NC}"
      STEPS_PASSED=$((STEPS_PASSED + 1))
      STEP_RESULTS["$name"]="pass"
      ;;
    fail)
      echo -e "  ${FAIL} ${RED}${name}${NC} ${DIM}(${duration}s)${NC}"
      if [[ -n "$detail" ]]; then
        echo -e "     ${DIM}${detail}${NC}"
      fi
      STEPS_FAILED=$((STEPS_FAILED + 1))
      STEP_RESULTS["$name"]="fail"
      ;;
    skip)
      echo -e "  ${SKIP} ${YELLOW}${name}${NC} ${DIM}— ${detail}${NC}"
      STEPS_SKIPPED=$((STEPS_SKIPPED + 1))
      STEP_RESULTS["$name"]="skip"
      ;;
    warn)
      echo -e "  ${WARN} ${YELLOW}${name}${NC} ${DIM}(${duration}s) — ${detail}${NC}"
      STEPS_PASSED=$((STEPS_PASSED + 1))
      STEP_RESULTS["$name"]="warn"
      ;;
  esac
  STEP_DURATIONS["$name"]="$duration"
}

run_step() {
  local name="$1"
  shift
  local start
  start=$(date +%s)

  if $VERBOSE; then
    if "$@"; then
      local end; end=$(date +%s)
      print_result "$name" "pass" "$((end - start))"
      return 0
    else
      local end; end=$(date +%s)
      print_result "$name" "fail" "$((end - start))"
      return 1
    fi
  else
    local output
    if output=$("$@" 2>&1); then
      local end; end=$(date +%s)
      print_result "$name" "pass" "$((end - start))"
      return 0
    else
      local end; end=$(date +%s)
      local last_lines
      last_lines=$(echo "$output" | tail -5)
      print_result "$name" "fail" "$((end - start))" "$last_lines"
      return 1
    fi
  fi
}

has_files() {
  local pattern="$1"
  local dir="${2:-.}"
  find "$dir" -type f -name "$pattern" \
    -not -path "*/node_modules/*" \
    -not -path "*/.git/*" \
    -not -path "*/.venv/*" \
    -not -path "*/venv/*" \
    -not -path "*/dist/*" \
    -print -quit 2>/dev/null | grep -q .
}

check_command() {
  command -v "$1" &>/dev/null
}

should_run() {
  local step="$1"
  if [[ -n "$SINGLE_STEP" ]]; then
    [[ "$SINGLE_STEP" == "$step" ]]
  else
    true
  fi
}

# =============================================================================
# PHASE 1: Format & Lint
# =============================================================================

run_phase_1() {
  print_header "PHASE 1: Format & Lint"

  local phase_failed=false

  # --- Prettier ---
  if should_run "format"; then
    print_step "Prettier" "formatting all files..."
    if check_command pnpm; then
      run_step "Prettier Format" pnpm format 2>/dev/null || phase_failed=true
    else
      print_result "Prettier Format" "skip" "0" "pnpm not installed"
    fi
  fi

  # --- ESLint ---
  if should_run "lint"; then
    if has_files "*.ts" || has_files "*.tsx" || has_files "*.js" || has_files "*.jsx"; then
      print_step "ESLint" "linting JS/TS files..."
      run_step "ESLint" pnpm lint:fix 2>/dev/null || phase_failed=true
    else
      print_result "ESLint" "skip" "0" "no JS/TS files found"
    fi
  fi

  # --- Markdownlint ---
  if should_run "lint-md"; then
    if has_files "*.md"; then
      print_step "Markdownlint" "checking markdown files..."
      run_step "Markdownlint" pnpm lint:md 2>/dev/null || phase_failed=true
    else
      print_result "Markdownlint" "skip" "0" "no markdown files"
    fi
  fi

  # --- Stylelint ---
  if should_run "lint-css"; then
    if has_files "*.css" || has_files "*.scss"; then
      print_step "Stylelint" "checking stylesheets..."
      run_step "Stylelint" pnpm lint:css 2>/dev/null || phase_failed=true
    else
      print_result "Stylelint" "skip" "0" "no CSS/SCSS files"
    fi
  fi

  # --- Python: ruff ---
  if should_run "lint"; then
    if has_files "*.py"; then
      print_step "Ruff" "linting Python files..."
      if check_command ruff; then
        run_step "Ruff Lint" ruff check . --fix --quiet || phase_failed=true
        run_step "Ruff Format" ruff format . --quiet || phase_failed=true
      else
        print_result "Ruff" "skip" "0" "ruff not installed (pip install ruff)"
      fi
    fi
  fi

  # --- Commitlint ---
  if should_run "commitlint"; then
    if git -C "${REPO_ROOT}" rev-parse HEAD~1 &>/dev/null; then
      print_step "Commitlint" "checking last commit message..."
      local cl_start; cl_start=$(date +%s)
      if pnpm commitlint 2>/dev/null; then
        local cl_end; cl_end=$(date +%s)
        print_result "Commitlint" "pass" "$((cl_end - cl_start))"
      else
        local cl_end; cl_end=$(date +%s)
        print_result "Commitlint" "warn" "$((cl_end - cl_start))" "commit message style"
      fi
    else
      print_result "Commitlint" "skip" "0" "not enough commit history"
    fi
  fi

  # --- TypeScript ---
  if should_run "typecheck"; then
    if [[ -f "${REPO_ROOT}/tsconfig.json" ]]; then
      print_step "TypeScript" "type-checking..."
      run_step "TypeScript" pnpm typecheck 2>/dev/null || phase_failed=true
    else
      print_result "TypeScript" "skip" "0" "no tsconfig.json"
    fi
  fi

  $phase_failed && return 1 || return 0
}

# =============================================================================
# PHASE 2: Tests & Builds
# =============================================================================

run_phase_2() {
  print_header "PHASE 2: Tests & Builds"

  local phase_failed=false

  # --- Link Check ---
  if should_run "link-check"; then
    if check_command lychee; then
      print_step "Link Check" "checking documentation links..."
      run_step "Link Check" lychee --no-progress "**/*.md" \
        --exclude-path node_modules \
        --exclude-path .git \
        || phase_failed=true
    else
      print_result "Link Check" "skip" "0" "lychee not installed (cargo install lychee)"
    fi
  fi

  # --- CrewAI Tests ---
  if should_run "test-crewai"; then
    if [[ -d "${REPO_ROOT}/.crewai/tests" ]]; then
      print_step "CrewAI Tests" "running pytest..."
      if check_command pytest; then
        run_step "CrewAI Tests" pytest "${REPO_ROOT}/.crewai/tests/" -v --tb=short || phase_failed=true
      else
        run_step "CrewAI Tests" python3 -m pytest "${REPO_ROOT}/.crewai/tests/" -v --tb=short || phase_failed=true
      fi
    else
      print_result "CrewAI Tests" "skip" "0" "no .crewai/tests/ directory"
    fi
  fi

  # --- Website Build ---
  if should_run "test-website" || should_run "build-website"; then
    if [[ -d "${REPO_ROOT}/website" ]]; then
      print_step "Website Build" "building website..."
      run_step "Website Build" pnpm --filter website run build || phase_failed=true
    else
      print_result "Website Build" "skip" "0" "no website/ directory"
    fi
  fi

  $phase_failed && return 1 || return 0
}

# =============================================================================
# PHASE 3: Deploy (skipped locally by default)
# =============================================================================

run_phase_3() {
  if ! $RUN_DEPLOY; then
    print_header "PHASE 3: Deploy"
    print_result "Preview Deploy" "skip" "0" "local mode (use --deploy to enable)"
    print_result "Production Deploy" "skip" "0" "local mode (use --deploy to enable)"
    return 0
  fi

  print_header "PHASE 3: Deploy"

  if ! check_env_for_deploy; then
    print_result "Deploy" "fail" "0" "missing Cloudflare credentials"
    return 1
  fi

  if ! check_command wrangler; then
    print_result "Deploy" "fail" "0" "wrangler not installed (npm i -g wrangler)"
    return 1
  fi

  print_step "Deploy" "deploying to Cloudflare Pages..."
  run_step "Cloudflare Deploy" wrangler pages deploy "${REPO_ROOT}/website/dist" \
    --project-name=website \
    --branch=local-preview \
    || return 1
}

# =============================================================================
# PHASE 4: CrewAI Review (optional)
# =============================================================================

run_phase_4() {
  if ! $RUN_REVIEW && ! should_run "review"; then
    print_header "PHASE 4: AI Code Review"
    print_result "CrewAI Review" "skip" "0" "use --review to enable"
    return 0
  fi

  print_header "PHASE 4: AI Code Review"

  if ! check_env_for_review; then
    print_result "CrewAI Review" "skip" "0" "OPENROUTER_API_KEY not provided"
    return 0
  fi

  # Clean workspace for idempotent run
  clean_workspace

  local is_git_repo=false
  local has_commits=false
  if git -C "${REPO_ROOT}" rev-parse --git-dir &>/dev/null; then
    is_git_repo=true
    if git -C "${REPO_ROOT}" rev-parse HEAD &>/dev/null; then
      has_commits=true
    fi
  fi

  if ! $is_git_repo; then
    print_result "CrewAI Review" "skip" "0" "not a git repository"
    return 0
  fi

  local crewai_dir="${REPO_ROOT}/.crewai"
  local workspace_dir="${crewai_dir}/workspace"
  mkdir -p "${workspace_dir}/trace"

  print_step "Diff Generation" "creating diff for review..."
  local diff_file="${workspace_dir}/diff.txt"
  local diff_source="unknown"
  local diff_size=0

  local has_working_changes=false
  local has_staged_changes=false
  if $has_commits; then
    if ! git -C "${REPO_ROOT}" diff --quiet 2>/dev/null; then
      has_working_changes=true
    fi
    if ! git -C "${REPO_ROOT}" diff --cached --quiet 2>/dev/null; then
      has_staged_changes=true
    fi
  fi

  if $has_working_changes || $has_staged_changes; then
    git -C "${REPO_ROOT}" diff HEAD > "${diff_file}" 2>/dev/null
    diff_size=$(wc -l < "${diff_file}")
    diff_source="working tree vs HEAD (uncommitted changes)"

  elif $has_commits; then
    local base_branch
    base_branch=$(git -C "${REPO_ROOT}" rev-parse --abbrev-ref HEAD 2>/dev/null)
    local default_base="main"
    if [[ "$base_branch" == "main" || "$base_branch" == "master" ]]; then
      default_base="HEAD~1"
    fi

    if git -C "${REPO_ROOT}" diff "${default_base}"...HEAD > "${diff_file}" 2>/dev/null; then
      diff_size=$(wc -l < "${diff_file}")
    fi

    if [[ "$diff_size" -eq 0 ]]; then
      git -C "${REPO_ROOT}" show HEAD > "${diff_file}" 2>/dev/null || true
      diff_size=$(wc -l < "${diff_file}")
      diff_source="last commit (git show HEAD)"
    else
      diff_source="branch diff (${default_base}...HEAD)"
    fi
  else
    git -C "${REPO_ROOT}" diff --cached > "${diff_file}" 2>/dev/null || true
    diff_size=$(wc -l < "${diff_file}")
    diff_source="staged changes (initial commit)"
  fi

  echo -e "  ${DIM}Source: ${diff_source}${NC}"
  echo -e "  ${DIM}Generated diff: ${diff_size} lines${NC}"

  if [[ "$diff_size" -eq 0 ]]; then
    echo -e "  ${WARN} No changes detected — nothing to review."
    print_result "CrewAI Review" "skip" "0" "no changes to review"
    return 0
  fi

  local commit_sha
  commit_sha=$(git -C "${REPO_ROOT}" rev-parse HEAD 2>/dev/null || echo "local")
  local repo_name
  repo_name=$(basename "${REPO_ROOT}")

  local changed_files
  if $has_working_changes || $has_staged_changes; then
    changed_files=$(git -C "${REPO_ROOT}" diff --name-only HEAD 2>/dev/null || echo "")
  elif $has_commits; then
    changed_files=$(git -C "${REPO_ROOT}" diff --name-only "${default_base}"...HEAD 2>/dev/null || git -C "${REPO_ROOT}" diff --name-only HEAD 2>/dev/null || echo "")
  else
    changed_files=$(git -C "${REPO_ROOT}" diff --cached --name-only 2>/dev/null || echo "")
  fi

  local additions deletions file_count
  if $has_working_changes || $has_staged_changes; then
    additions=$(git -C "${REPO_ROOT}" diff --numstat HEAD 2>/dev/null | awk '{s+=$1} END {print s+0}')
    deletions=$(git -C "${REPO_ROOT}" diff --numstat HEAD 2>/dev/null | awk '{s+=$2} END {print s+0}')
  elif $has_commits; then
    additions=$(git -C "${REPO_ROOT}" diff --numstat "${default_base}"...HEAD 2>/dev/null | awk '{s+=$1} END {print s+0}' || echo "0")
    deletions=$(git -C "${REPO_ROOT}" diff --numstat "${default_base}"...HEAD 2>/dev/null | awk '{s+=$2} END {print s+0}' || echo "0")
  else
    additions=$(git -C "${REPO_ROOT}" diff --cached --numstat 2>/dev/null | awk '{s+=$1} END {print s+0}' || echo "0")
    deletions=$(git -C "${REPO_ROOT}" diff --cached --numstat 2>/dev/null | awk '{s+=$2} END {print s+0}' || echo "0")
  fi
  file_count=$(echo "$changed_files" | grep -c . || echo "0")

  local review_labels_json="[]"
  if $RUN_FULL_REVIEW; then
    review_labels_json='["crewai:full-review"]'
    echo -e "  ${DIM}Labels: crewai:full-review (all 9 specialist crews)${NC}"
  elif [[ -n "$REVIEW_LABELS" ]]; then
    review_labels_json=$(echo "$REVIEW_LABELS" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read().strip().split(',')))")
    echo -e "  ${DIM}Labels: ${REVIEW_LABELS}${NC}"
  fi

  python3 -c "
import json, sys
files = [f for f in '''${changed_files}'''.strip().split('\n') if f]
data = {
    'pr_number': 'local',
    'commit_sha': '${commit_sha}',
    'labels': ${review_labels_json},
    'files_changed': ${file_count},
    'additions': ${additions},
    'deletions': ${deletions},
    'file_list': files,
}
with open('${workspace_dir}/diff.json', 'w') as f:
    json.dump(data, f, indent=2)
" 2>/dev/null || true

  local commit_messages
  commit_messages=$(git -C "${REPO_ROOT}" log --oneline -5 2>/dev/null || echo "local run")
  python3 -c "
import json
msgs = '''${commit_messages}'''.strip().split('\n')
data = {'commit_count': len(msgs), 'commit_messages': msgs}
with open('${workspace_dir}/commits.json', 'w') as f:
    json.dump(data, f, indent=2)
" 2>/dev/null || true

  export PR_NUMBER="local"
  export COMMIT_SHA="${commit_sha}"
  export GITHUB_REPOSITORY="local/${repo_name}"
  export GITHUB_WORKSPACE="${REPO_ROOT}"
  export CORE_CI_RESULT="success"

  # Run CrewAI
  print_step "CrewAI Review" "running AI code review..."
  local start
  start=$(date +%s)

  if (cd "${crewai_dir}" && python3 main.py) 2>&1 | {
    if $VERBOSE; then
      cat
    else
      while IFS= read -r line; do
        case "$line" in
          *"STEP"*|*"✅"*|*"❌"*|*"⚠️"*|*"🔬"*|*"complete"*)
            echo -e "     ${DIM}${line}${NC}"
            ;;
        esac
      done
    fi
  }; then
    local end; end=$(date +%s)
    print_result "CrewAI Review" "pass" "$((end - start))"
  else
    local end; end=$(date +%s)
    print_result "CrewAI Review" "fail" "$((end - start))"
    return 1
  fi

  # Display summary if it exists
  local summary_file="${workspace_dir}/final_summary.md"
  if [[ -f "$summary_file" ]]; then
    echo ""
    echo -e "${CYAN}${BOLD}  ┌─ Review Summary ───────────────────────────────────┐${NC}"
    head -30 "$summary_file" | while IFS= read -r line; do
      echo -e "${CYAN}  │${NC} $line"
    done
    local total_lines
    total_lines=$(wc -l < "$summary_file")
    if [[ "$total_lines" -gt 30 ]]; then
      echo -e "${CYAN}  │${NC} ${DIM}... ($((total_lines - 30)) more lines in .crewai/workspace/final_summary.md)${NC}"
    fi
    echo -e "${CYAN}  └──────────────────────────────────────────────────────┘${NC}"
    echo ""
    echo -e "  ${DIM}Full review: .crewai/workspace/final_summary.md${NC}"
    echo -e "  ${DIM}All outputs: .crewai/workspace/*.json${NC}"
  fi
}

# =============================================================================
# Summary
# =============================================================================

print_summary() {
  local total_end
  total_end=$(date +%s)
  local total_duration=$((total_end - TOTAL_START))

  echo ""
  echo -e "${BOLD}${BLUE}${PHASE}${PHASE}${PHASE}${PHASE}${PHASE}${PHASE}${PHASE}${PHASE}${PHASE}${NC}"
  echo -e "${BOLD}  📊 CI Results${NC}"
  echo -e "${BOLD}${BLUE}${PHASE}${PHASE}${PHASE}${PHASE}${PHASE}${PHASE}${PHASE}${PHASE}${PHASE}${NC}"
  echo ""

  printf "  ${BOLD}%-24s %-10s %s${NC}\n" "Step" "Status" "Duration"
  printf "  %-24s %-10s %s\n" "────────────────────────" "──────────" "────────"

  for step in "${!STEP_RESULTS[@]}"; do
    local status="${STEP_RESULTS[$step]}"
    local duration="${STEP_DURATIONS[$step]:-0}"
    local status_icon

    case "$status" in
      pass) status_icon="${GREEN}${PASS} pass${NC}" ;;
      fail) status_icon="${RED}${FAIL} FAIL${NC}" ;;
      skip) status_icon="${YELLOW}${SKIP}skip${NC}" ;;
      warn) status_icon="${YELLOW}${WARN} warn${NC}" ;;
    esac

    printf "  %-24s %b %s\n" "$step" "$status_icon" "${DIM}${duration}s${NC}"
  done

  echo ""
  echo -e "  ${GREEN}Passed: ${STEPS_PASSED}${NC}  ${RED}Failed: ${STEPS_FAILED}${NC}  ${YELLOW}Skipped: ${STEPS_SKIPPED}${NC}  ${DIM}Total: ${total_duration}s${NC}"
  echo ""

  if [[ $STEPS_FAILED -gt 0 ]]; then
    echo -e "  ${RED}${BOLD}${FAIL} CI FAILED${NC}"
    return 1
  else
    echo -e "  ${GREEN}${BOLD}${PASS} CI PASSED${NC}"
    return 0
  fi
}

# =============================================================================
# Main
# =============================================================================

main() {
  cd "${REPO_ROOT}"

  echo ""
  echo -e "${BOLD}${BLUE}  🚀 Local CI Runner${NC}"
  echo -e "${DIM}  Same pipeline as GitHub Actions — minus the cloud.${NC}"
  echo -e "${DIM}  $(date '+%Y-%m-%d %H:%M:%S')${NC}"

  # Check required tools
  check_dependencies

  # Single step mode
  if [[ -n "$SINGLE_STEP" ]]; then
    print_header "Running: ${SINGLE_STEP}"
    case "$SINGLE_STEP" in
      format|lint|lint-md|lint-css|typecheck|commitlint)
        run_phase_1 || true ;;
      link-check|test-crewai|test-website|build-website)
        run_phase_2 || true ;;
      review)
        RUN_REVIEW=true
        run_phase_4 || true ;;
      deploy)
        RUN_DEPLOY=true
        run_phase_3 || true ;;
      *)
        echo -e "${RED}Unknown step: ${SINGLE_STEP}${NC}"
        exit 1 ;;
    esac
    print_summary
    return $?
  fi

  # Full pipeline
  run_phase_1 || true
  run_phase_2 || true
  run_phase_3 || true
  run_phase_4 || true

  print_summary
}

main "$@"
