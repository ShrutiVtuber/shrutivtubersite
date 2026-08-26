#!/usr/bin/env bash
# Put a secret into .env without it passing through a chat, a shell history or
# a terminal scrollback.
#
#   ./scripts/set-secret.sh SHRUTI_STRIPE_SECRET_KEY
#   ./scripts/set-secret.sh SHRUTI_TWITCH_CLIENT_SECRET
#
# The value is read with the echo off, so it never appears on screen and never
# reaches ~/.bash_history — which a `sed -i` or an inline export would not
# manage. It is written straight into .env, and .env is gitignored.
#
# It also CHECKS THE SHAPE. Every key here has a recognisable prefix, and the
# common mistake is pasting a credential that looks secret and is the wrong
# one — a Twitch stream key where a client secret goes, or a live Stripe key
# during testing. A prefix check catches that in the second it happens rather
# than at the moment somebody tries to pay.
set -euo pipefail
cd "$(dirname "$0")/.."

KEY="${1:-}"
if [[ -z "$KEY" ]]; then
  echo "usage: $0 SHRUTI_SOMETHING" >&2
  exit 2
fi

# key name -> "expected-prefix|what it is|where to find it"
declare -A EXPECT=(
  [SHRUTI_STRIPE_SECRET_KEY]="sk_|Stripe secret key|dashboard.stripe.com/test/apikeys"
  [SHRUTI_STRIPE_PUBLISHABLE_KEY]="pk_|Stripe publishable key|dashboard.stripe.com/test/apikeys"
  [SHRUTI_STRIPE_WEBHOOK_SECRET]="whsec_|Stripe webhook signing secret|dashboard.stripe.com/test/webhooks"
  [SHRUTI_STRIPE_PRICE_LAMPLIGHTER]="price_|Stripe price ID|dashboard.stripe.com/test/products"
  [SHRUTI_STRIPE_PRICE_ALMANAC]="price_|Stripe price ID|dashboard.stripe.com/test/products"
  [SHRUTI_TWITCH_CLIENT_ID]="|Twitch application Client ID|dev.twitch.tv/console/apps"
  [SHRUTI_TWITCH_CLIENT_SECRET]="|Twitch application Client Secret|dev.twitch.tv/console/apps"
  [SHRUTI_YOUTUBE_API_KEY]="AIza|YouTube Data API key|console.cloud.google.com/apis/credentials"
  [SHRUTI_RESEND_API_KEY]="re_|Resend API key|resend.com/api-keys"
  [SHRUTI_SECRET_KEY]="|session signing secret|anything long and random"
  [SHRUTI_DISCORD_BOT_TOKEN]="|Discord BOT TOKEN|discord.com/developers → your app → Bot → Reset Token"
  [SHRUTI_DISCORD_CLIENT_SECRET]="|Discord app Client Secret|discord.com/developers → your app → OAuth2"
)

if [[ -n "${EXPECT[$KEY]:-}" ]]; then
  IFS='|' read -r PREFIX WHAT WHERE <<<"${EXPECT[$KEY]}"
  echo "  $WHAT"
  echo "  from $WHERE"
else
  PREFIX=""; WHAT="$KEY"
  echo "  $KEY (not a key this script knows — no shape check)"
fi

printf '  paste it (nothing will appear): '
read -rs VALUE
echo
VALUE="${VALUE#"${VALUE%%[![:space:]]*}"}"
VALUE="${VALUE%"${VALUE##*[![:space:]]}"}"

if [[ -z "$VALUE" ]]; then
  echo "  nothing pasted — .env not touched" >&2
  exit 1
fi

# A Twitch STREAM key is the credential most likely to be confused for a
# secret: it is secret, it is on the Twitch dashboard, and it is completely
# the wrong one. It broadcasts to her channel and can do nothing else.
if [[ "$VALUE" == live_* && "$KEY" == SHRUTI_TWITCH_* ]]; then
  echo "  REFUSED. That is a Twitch STREAM key — the one OBS broadcasts with." >&2
  echo "  Anyone holding it can stream to the channel. Reset it in the Twitch" >&2
  echo "  dashboard, then get a Client ID and Secret from dev.twitch.tv instead." >&2
  exit 1
fi

# Discord tokens have no fixed prefix, so shape is the only check available:
# three dot-separated parts, the first being the app id in base64. The mistake
# this catches is the common one — pasting the APPLICATION ID or the PUBLIC KEY
# where the token goes. Both are on the same page, neither is secret, and
# neither works.
if [[ "$KEY" == SHRUTI_DISCORD_BOT_TOKEN ]]; then
  if [[ "$VALUE" != *.*.* ]]; then
    echo "  REFUSED. A Discord bot token has three dot-separated parts." >&2
    echo "  That looks like the Application ID or the Public Key — those are" >&2
    echo "  on the same page, are not secret, and will not authenticate." >&2
    echo "  The token is under Bot → Reset Token, and is shown ONCE." >&2
    exit 1
  fi
fi

if [[ -n "$PREFIX" && "$VALUE" != "$PREFIX"* ]]; then
  echo "  REFUSED. A $WHAT starts with '$PREFIX' and this does not." >&2
  echo "  .env not touched." >&2
  exit 1
fi

if [[ "$VALUE" == sk_live_* || "$VALUE" == pk_live_* ]]; then
  echo
  echo "  That is a LIVE Stripe key. Real cards, real money."
  printf '  type "live" to confirm: '
  read -r CONFIRM
  [[ "$CONFIRM" == "live" ]] || { echo "  stopped. .env not touched." >&2; exit 1; }
fi

touch .env
if grep -qE "^${KEY}=" .env; then
  # A temp file rather than `sed -i "s|=$VALUE|"`, because the value would be
  # part of the command and land in the process list for anyone reading it.
  TMP="$(mktemp)"
  trap 'rm -f "$TMP"' EXIT
  KEY="$KEY" VALUE="$VALUE" awk '
    BEGIN { k = ENVIRON["KEY"]; v = ENVIRON["VALUE"] }
    $0 ~ "^" k "=" { print k "=" v; done = 1; next }
    { print }
    END { if (!done) print k "=" v }
  ' .env > "$TMP"
  cat "$TMP" > .env
else
  KEY="$KEY" VALUE="$VALUE" awk 'BEGIN { print ENVIRON["KEY"] "=" ENVIRON["VALUE"] }' >> .env
fi

echo "  set ${KEY} (${#VALUE} characters). .env is gitignored."
echo "  restart to pick it up:  docker compose up -d backend"
