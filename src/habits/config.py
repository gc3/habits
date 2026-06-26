# ----------- Configuration ----------------------------------------------------
"""
  Resolve XDG base directories and load the habits rc file. This is the single
  source of truth for where config and habit data live on disk.
"""

import os
import configparser

# ----------- Internal Helpers -------------------------------------------------
_APP = "habits"

def _xdg_dir(env_var, default_subpath):
  """
    return $env_var/APP, falling back to ~/default_subpath/APP when unset
  """
  base = os.environ.get(env_var)
  if not base:
    base = os.path.join(os.path.expanduser("~"), default_subpath)

  return os.path.join(base, _APP)


# ----------- External API -----------------------------------------------------
# Configuration directories ( ~/.config/habits)
CONFIG_DIR  = _xdg_dir("XDG_CONFIG_HOME", ".config")
CONFIG_FILE = os.path.join(CONFIG_DIR, "habitsrc")

# Data directories (~/.local/share/habits )
DATA_DIR = _xdg_dir("XDG_DATA_HOME", os.path.join(".local", "share"))
DEFAULT_STORAGE_DIR = DATA_DIR
ARCHIVED_STORAGE_DIR = ".archive"

def parse_config():
  """
    from the rc file load variables into a dictionary for the caller
  """
  if not os.path.exists(CONFIG_FILE):
    return None

  config = configparser.ConfigParser(allow_unnamed_section=True)
  with open(CONFIG_FILE, encoding="utf-8") as f:
    config.read_file(f)

  # NOTE -- error check the actual entries . like no / at path's end
  return dict(config[configparser.UNNAMED_SECTION])

def ensure_storage(storage_dir):
  """
    create the storage dir and its archive subdir if they don't exist. safe to
    call repeatedly. operates on the resolved storage_dir so a configured
    'storage_dir' override is honored, not just the default.
  """
  os.makedirs(storage_dir, exist_ok=True)
  os.makedirs(os.path.join(storage_dir, ARCHIVED_STORAGE_DIR), exist_ok=True)

def resolve_storage_dir(cfg):
  """
    the configured 'storage_dir' (with a leading ~ expanded) or the default.
    does not create it -- call ensure_storage for that.
  """
  configured = cfg.get('storage_dir') if cfg else None
  if configured:
    return os.path.expanduser(configured)

  return DEFAULT_STORAGE_DIR

def load_api_token(cfg):
  """
    resolve the Todoist API token from the file named by 'api_token_file' in
    the rc config, so the secret stays out of the (public) config file itself.
    returns the stripped token, or None when no token file is configured.
    raises OSError if a configured token file cannot be read (fail loud on a
    real misconfiguration rather than silently skipping sync).
  """
  if not cfg:
    return None

  token_path = cfg.get('api_token_file')
  if not token_path:
    return None

  with open(os.path.expanduser(token_path), encoding="utf-8") as f:
    return f.read().strip() or None
