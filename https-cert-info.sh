#! /bin/bash

# Get certificate details about the specified domain via HTTPS

HOST="$1"

# Remove the first argument
shift

OPENSSL_OPTS="$@"

if [ -z "$HOST" ]; then
	echo "Usage: $0 <host> [openssl options]"
	exit 1
fi

if [ -z "$OPENSSL_OPTS" ]; then
	OPENSSL_OPTS="-noout -text"
fi

echo | openssl s_client -servername ${HOST} -connect ${HOST}:443 2>/dev/null | sed -ne "/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p" | openssl x509 ${OPENSSL_OPTS}
