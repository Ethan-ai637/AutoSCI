# Environment and Execution

## Environment layers

Keep three concepts separate:

1. **declared environment** — what authors/documentation state;
2. **resolved environment** — what dependency solver/install actually produced;
3. **runtime environment** — what the successful/failed process actually saw.

A reproduction may use the same package names but still differ in CUDA, compiler, BLAS, GPU architecture, driver, or OS.

## Capture useful state

Capture when relevant:

- OS/platform;
- Python implementation/version;
- package versions;
- GPU model/visibility;
- CUDA/runtime/driver hints;
- compiler version;
- environment manager;
- selected safe environment variables;
- externally required binaries.

Do not dump the full process environment because it may contain secrets.

`run_with_ledger.py` passes a small runtime-variable allowlist to repository commands and records the names that were visible. Add `--env NAME` only for a reviewed, non-secret variable required by the command. It refuses common credential-like names such as tokens, passwords, API keys, cookies, and SSH variables. This reduces environment-variable exposure; it does not sandbox filesystem access. Run untrusted code in a disposable/isolated environment without sensitive files or mounts. If the command needs credentials to access an artifact, retrieve the artifact through a separately reviewed channel instead of handing credentials to untrusted repository code.

## Untrusted repository code

Before executing repository-controlled code, inspect:

- `setup.py`, build backend hooks, custom `pyproject.toml` build steps;
- shell/PowerShell scripts;
- Dockerfiles and entrypoints;
- Makefiles;
- Git hooks/submodules;
- download/install scripts;
- code that invokes shell/network/cloud tooling.

Prefer disposable/isolated environments. Avoid privileged execution and avoid mounting sensitive directories into containers.

## Resource guard

Before full training, record a coarse resource plan:

- accelerator required;
- expected GPU memory class;
- CPU/RAM/storage class;
- dataset/checkpoint size;
- expected duration class;
- number of runs/seeds.

If the environment cannot satisfy the plan, classify the blocker. Do not pretend a smaller surrogate run reproduces the full claim unless the contract explicitly targets that surrogate.
