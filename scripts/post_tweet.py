#!/usr/bin/env python3
"""
Post a tweet using Tweepy.

Spec references (Prime Directive compliance):
- See [specs/_meta.md](specs/_meta.md) — "All outward-facing outputs (external publication, public APIs, or user-visible messages) are gated by a dedicated `Judge` agent. The `Judge` acts as the final safety gatekeeper and must explicitly approve content before it leaves the system." 
- See [specs/technical.md](specs/technical.md) — API auth and observability guidance (e.g., `Authorization: Bearer <token>` and `trace_id`).

Usage:
  pip install tweepy
  export TW_CONSUMER_KEY=...
  export TW_CONSUMER_SECRET=...
  export TW_ACCESS_TOKEN=...
  export TW_ACCESS_TOKEN_SECRET=...
  # Either set JUDGE_APPROVED=1 or pass --judge-approved
  python scripts/post_tweet.py --text "Hello world" --judge-approved

This script enforces a Judge-approval check per `specs/_meta.md` before posting.
"""
import os
import sys
import argparse
import tweepy


def require_judge_approval(args):
    env_ok = os.getenv('JUDGE_APPROVED') == '1'
    if args.judge_approved or env_ok:
        return True
    print("Aborting: outward-facing outputs require Judge approval per specs/_meta.md")
    print("Set the environment variable JUDGE_APPROVED=1 or pass --judge-approved to proceed.")
    return False


def load_creds():
    return {
        'consumer_key': os.getenv('TW_CONSUMER_KEY'),
        'consumer_secret': os.getenv('TW_CONSUMER_SECRET'),
        'access_token': os.getenv('TW_ACCESS_TOKEN'),
        'access_token_secret': os.getenv('TW_ACCESS_TOKEN_SECRET'),
    }


def validate_creds(creds):
    missing = [k for k, v in creds.items() if not v]
    if missing:
        print('Missing Twitter credentials:', ', '.join(missing))
        print('Set the environment variables listed in the script header.')
        return False
    return True


def post_tweet(text, creds):
    client = tweepy.Client(
        consumer_key=creds['consumer_key'],
        consumer_secret=creds['consumer_secret'],
        access_token=creds['access_token'],
        access_token_secret=creds['access_token_secret'],
    )
    try:
        resp = client.create_tweet(text=text)
        print('Tweet posted. id=', getattr(resp.data, 'id', None))
        return resp
    except Exception as e:
        print('Failed to post tweet:', str(e))
        raise


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--text', required=True, help='Tweet text')
    p.add_argument('--judge-approved', action='store_true', help='Bypass env var check (still requires explicit approval)')
    args = p.parse_args()

    if not require_judge_approval(args):
        sys.exit(2)

    creds = load_creds()
    if not validate_creds(creds):
        sys.exit(3)

    post_tweet(args.text, creds)


if __name__ == '__main__':
    main()
