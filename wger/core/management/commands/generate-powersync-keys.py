# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

# Standard Library
import json
from base64 import urlsafe_b64encode

# Django
from django.core.management.base import BaseCommand

# Third Party
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
)
from jose import jwk


class Command(BaseCommand):
    """
    Generates a fresh RS256 keypair for PowerSync JWT signing.
    """

    help = (
        'Generate a fresh RS256 keypair for PowerSync JWT signing/verification. '
        'The output can be pasted into the docker compose env file.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--kid',
            default='powersync',
            help='Key ID written into the JWK and the JWT header (default: powersync).',
        )
        parser.add_argument(
            '--key-size',
            type=int,
            default=2048,
            help='RSA key size in bits (default: 2048).',
        )

    def handle(self, *args, **options):
        kid = options['kid']
        key_size = options['key_size']

        # Generate RSA keypair via cryptography (python-jose's `jwk.construct`
        # consumes a PEM string).
        rsa_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
        priv_pem = rsa_key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NoEncryption(),
        )

        # Convert to JWK; jose returns bytes for the encoded values, normalise to str.
        jose_key = jwk.construct(priv_pem.decode(), algorithm='RS256')
        priv_jwk = {
            k: (v.decode() if isinstance(v, bytes) else v) for k, v in jose_key.to_dict().items()
        }
        priv_jwk['alg'] = 'RS256'
        priv_jwk['kid'] = kid

        # Public JWK keeps only the public components.
        pub_jwk = {k: priv_jwk[k] for k in ('kty', 'n', 'e', 'alg', 'kid')}

        def b64_jwk(d):
            return urlsafe_b64encode(json.dumps(d).encode()).decode()

        self.stdout.write(
            self.style.WARNING(
                '# Paste these into your environment file (e.g. docker/config/prod.env).\n'
                '# Keep POWERSYNC_JWKS_PRIVATE_KEY secret — never commit it to a public repo.'
            )
        )
        self.stdout.write('')
        self.stdout.write(f'POWERSYNC_JWKS_PRIVATE_KEY={b64_jwk(priv_jwk)}')
        self.stdout.write(f'POWERSYNC_JWKS_PUBLIC_KEY={b64_jwk(pub_jwk)}')
