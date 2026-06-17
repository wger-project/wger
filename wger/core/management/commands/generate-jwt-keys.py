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
from jwt.algorithms import RSAAlgorithm


class Command(BaseCommand):
    """
    Generates a fresh RS256 keypair for JWT signing.

    The same key is used by SimpleJWT, allauth.headless, and the PowerSync
    token endpoint; the JWT 'aud' claim separates the use cases.
    """

    help = (
        'Generate a fresh RS256 keypair for JWT signing/verification (SimpleJWT, '
        'allauth.headless, PowerSync). The output can be pasted into the docker '
        'compose env file.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--kid',
            default='wger',
            help='Key ID written into the JWK and the JWT header (default: wger).',
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

        # Generate an RSA keypair and export it as a JWK.
        rsa_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
        priv_jwk = json.loads(RSAAlgorithm.to_jwk(rsa_key))
        priv_jwk['alg'] = 'RS256'
        priv_jwk['kid'] = kid

        # Public JWK keeps only the public components.
        pub_jwk = {k: priv_jwk[k] for k in ('kty', 'n', 'e', 'alg', 'kid')}

        def b64_jwk(d):
            return urlsafe_b64encode(json.dumps(d).encode()).decode()

        self.stdout.write(
            self.style.WARNING(
                '# Paste these into your environment file (e.g. docker/config/prod.env).\n'
                '# Keep JWT_PRIVATE_KEY secret, never commit it to a public repo.'
            )
        )
        self.stdout.write('')
        self.stdout.write(f'JWT_PRIVATE_KEY={b64_jwk(priv_jwk)}')
        self.stdout.write(f'JWT_PUBLIC_KEY={b64_jwk(pub_jwk)}')
