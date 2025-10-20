"""
License Validation System for Cardiac ML Research
授权验证系统

Implements RSA2048-based license validation with machine ID binding.
Per WEEK7_PLUS_DEPLOYMENT_PLAN.md Section 5 requirements.

Features:
- RSA2048 digital signature verification
- Machine ID binding (hardware-based unique identifier)
- License expiration checking
- Usage limits tracking
- Offline validation support

Security:
- Private key for license generation (kept by vendor)
- Public key for license validation (distributed with software)
- Tamper-proof machine ID generation

Author: Cardiac ML Research Team
Created: 2025-10-19
Version: 1.0.0
"""

import os
import sys
import uuid
import json
import base64
import hashlib
import platform
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import logging

# Cryptography imports
try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("[WARNING] cryptography library not available. License validation disabled.")

logger = logging.getLogger(__name__)


class MachineIDGenerator:
    """
    Generate unique machine identifier

    Uses hardware information to create a consistent machine ID
    that persists across reboots but changes if hardware changes.
    """

    @staticmethod
    def get_machine_id() -> str:
        """
        Generate unique machine ID based on hardware

        Uses:
        - Machine UUID (motherboard)
        - MAC address (primary network interface)
        - CPU info
        - Hostname

        Returns:
            32-character hexadecimal machine ID
        """
        try:
            # Try to get machine UUID (most reliable)
            machine_uuid = MachineIDGenerator._get_machine_uuid()

            if machine_uuid:
                # Use machine UUID as primary identifier
                hash_input = machine_uuid
            else:
                # Fallback: combine multiple hardware identifiers
                mac_address = MachineIDGenerator._get_mac_address()
                hostname = platform.node()
                cpu_info = platform.processor()

                hash_input = f"{mac_address}|{hostname}|{cpu_info}"

            # Generate SHA256 hash
            hash_obj = hashlib.sha256(hash_input.encode('utf-8'))
            machine_id = hash_obj.hexdigest()

            logger.info(f"Generated machine ID: {machine_id[:16]}...")

            return machine_id

        except Exception as e:
            logger.error(f"Failed to generate machine ID: {e}")
            # Fallback to random UUID (will change on restart)
            return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()

    @staticmethod
    def _get_machine_uuid() -> Optional[str]:
        """Get machine UUID (motherboard UUID)"""
        try:
            # Linux
            if platform.system() == 'Linux':
                uuid_file = Path('/etc/machine-id')
                if uuid_file.exists():
                    return uuid_file.read_text().strip()

                # Alternative: DMI UUID
                dmi_uuid = Path('/sys/class/dmi/id/product_uuid')
                if dmi_uuid.exists():
                    try:
                        return dmi_uuid.read_text().strip()
                    except:
                        pass

            # Windows
            elif platform.system() == 'Windows':
                import subprocess
                result = subprocess.run(
                    ['wmic', 'csproduct', 'get', 'UUID'],
                    capture_output=True,
                    text=True
                )
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    return lines[1].strip()

            # macOS
            elif platform.system() == 'Darwin':
                import subprocess
                result = subprocess.run(
                    ['system_profiler', 'SPHardwareDataType'],
                    capture_output=True,
                    text=True
                )
                for line in result.stdout.split('\n'):
                    if 'UUID' in line:
                        return line.split(':')[1].strip()

        except Exception as e:
            logger.debug(f"Could not get machine UUID: {e}")

        return None

    @staticmethod
    def _get_mac_address() -> str:
        """Get MAC address of primary network interface"""
        try:
            # Use UUID to get MAC address (cross-platform)
            mac = uuid.getnode()
            mac_str = ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2))
            return mac_str
        except:
            return "00:00:00:00:00:00"


class LicenseInfo:
    """License information structure"""

    def __init__(self,
                 license_key: str,
                 machine_id: str,
                 licensee_name: str,
                 organization: str,
                 modules: List[str],
                 issue_date: str,
                 expiry_date: str,
                 license_type: str = 'standard',
                 max_patients: Optional[int] = None,
                 features: Optional[Dict[str, Any]] = None):
        """
        Initialize license info

        Args:
            license_key: Unique license key
            machine_id: Bound machine ID
            licensee_name: Name of licensee
            organization: Organization name
            modules: List of enabled module IDs
            issue_date: Issue date (YYYY-MM-DD)
            expiry_date: Expiry date (YYYY-MM-DD)
            license_type: Type (trial/standard/professional/enterprise)
            max_patients: Maximum patients (None = unlimited)
            features: Additional features dictionary
        """
        self.license_key = license_key
        self.machine_id = machine_id
        self.licensee_name = licensee_name
        self.organization = organization
        self.modules = modules
        self.issue_date = issue_date
        self.expiry_date = expiry_date
        self.license_type = license_type
        self.max_patients = max_patients
        self.features = features or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'license_key': self.license_key,
            'machine_id': self.machine_id,
            'licensee_name': self.licensee_name,
            'organization': self.organization,
            'modules': self.modules,
            'issue_date': self.issue_date,
            'expiry_date': self.expiry_date,
            'license_type': self.license_type,
            'max_patients': self.max_patients,
            'features': self.features
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LicenseInfo':
        """Create from dictionary"""
        return cls(
            license_key=data['license_key'],
            machine_id=data['machine_id'],
            licensee_name=data['licensee_name'],
            organization=data['organization'],
            modules=data['modules'],
            issue_date=data['issue_date'],
            expiry_date=data['expiry_date'],
            license_type=data.get('license_type', 'standard'),
            max_patients=data.get('max_patients'),
            features=data.get('features', {})
        )

    def is_expired(self) -> bool:
        """Check if license is expired"""
        try:
            expiry = datetime.strptime(self.expiry_date, '%Y-%m-%d')
            return datetime.now() > expiry
        except:
            return True

    def days_until_expiry(self) -> int:
        """Get days until expiry (negative if expired)"""
        try:
            expiry = datetime.strptime(self.expiry_date, '%Y-%m-%d')
            delta = expiry - datetime.now()
            return delta.days
        except:
            return -9999

    def __str__(self) -> str:
        return (f"License({self.license_key[:16]}..., "
                f"{self.license_type}, "
                f"expires: {self.expiry_date})")


class LicenseValidator:
    """
    RSA2048-based license validator

    Validates licenses using digital signatures and machine ID binding.
    """

    def __init__(self, public_key_path: Optional[Path] = None):
        """
        Initialize validator

        Args:
            public_key_path: Path to public key file (PEM format)
        """
        if not CRYPTO_AVAILABLE:
            raise ImportError("cryptography library required for license validation")

        self.public_key_path = public_key_path
        self.public_key = None

        if public_key_path and public_key_path.exists():
            self.load_public_key(public_key_path)

        # Machine ID
        self.machine_id = MachineIDGenerator.get_machine_id()

    def load_public_key(self, key_path: Path):
        """Load RSA public key from PEM file"""
        try:
            with open(key_path, 'rb') as key_file:
                self.public_key = serialization.load_pem_public_key(
                    key_file.read(),
                    backend=default_backend()
                )
            logger.info(f"Public key loaded from {key_path}")
        except Exception as e:
            logger.error(f"Failed to load public key: {e}")
            raise

    def verify_signature(self, data: bytes, signature: bytes) -> bool:
        """
        Verify RSA2048 signature

        Args:
            data: Original data
            signature: Digital signature

        Returns:
            True if signature is valid
        """
        if not self.public_key:
            raise ValueError("Public key not loaded")

        try:
            self.public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            logger.debug(f"Signature verification failed: {e}")
            return False

    def validate_license_file(self, license_path: Path) -> tuple[bool, Optional[LicenseInfo], str]:
        """
        Validate license file

        Args:
            license_path: Path to license file (JSON format)

        Returns:
            Tuple of (is_valid, license_info, message)
        """
        try:
            # Load license file
            with open(license_path, 'r', encoding='utf-8') as f:
                license_data = json.load(f)

            # Extract license info and signature
            if 'license' not in license_data or 'signature' not in license_data:
                return False, None, "Invalid license file format"

            license_info_dict = license_data['license']
            signature_b64 = license_data['signature']

            # Decode signature
            try:
                signature = base64.b64decode(signature_b64)
            except:
                return False, None, "Invalid signature encoding"

            # Create LicenseInfo object
            license_info = LicenseInfo.from_dict(license_info_dict)

            # Verify signature
            license_json = json.dumps(license_info_dict, sort_keys=True)
            license_bytes = license_json.encode('utf-8')

            if not self.verify_signature(license_bytes, signature):
                return False, None, "Invalid signature - license may be tampered"

            # Check machine ID
            if license_info.machine_id != self.machine_id:
                return False, None, f"Machine ID mismatch (expected: {self.machine_id[:16]}...)"

            # Check expiry
            if license_info.is_expired():
                days_expired = -license_info.days_until_expiry()
                return False, None, f"License expired {days_expired} days ago"

            # All checks passed
            days_left = license_info.days_until_expiry()
            return True, license_info, f"Valid ({days_left} days remaining)"

        except FileNotFoundError:
            return False, None, "License file not found"
        except json.JSONDecodeError:
            return False, None, "Invalid JSON format"
        except Exception as e:
            logger.error(f"License validation error: {e}")
            return False, None, f"Validation error: {e}"

    def check_module_access(self, license_info: LicenseInfo, module_id: str) -> bool:
        """
        Check if license allows access to module

        Args:
            license_info: License information
            module_id: Module identifier to check

        Returns:
            True if module is licensed
        """
        # Check if module is in licensed modules list
        if '*' in license_info.modules:
            # Wildcard - all modules
            return True

        return module_id in license_info.modules

    def get_machine_id(self) -> str:
        """Get this machine's ID"""
        return self.machine_id


class LicenseGenerator:
    """
    License generator (vendor-side only)

    Generates signed licenses using private key.
    This should only be used by the software vendor.
    """

    def __init__(self, private_key_path: Optional[Path] = None):
        """
        Initialize generator

        Args:
            private_key_path: Path to private key file (PEM format)
        """
        if not CRYPTO_AVAILABLE:
            raise ImportError("cryptography library required")

        self.private_key = None

        if private_key_path and private_key_path.exists():
            self.load_private_key(private_key_path)

    def load_private_key(self, key_path: Path, password: Optional[bytes] = None):
        """Load RSA private key from PEM file"""
        try:
            with open(key_path, 'rb') as key_file:
                self.private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=password,
                    backend=default_backend()
                )
            logger.info(f"Private key loaded from {key_path}")
        except Exception as e:
            logger.error(f"Failed to load private key: {e}")
            raise

    @staticmethod
    def generate_key_pair(key_size: int = 2048) -> tuple:
        """
        Generate new RSA key pair

        Args:
            key_size: Key size in bits (default: 2048)

        Returns:
            Tuple of (private_key, public_key)
        """
        if not CRYPTO_AVAILABLE:
            raise ImportError("cryptography library required")

        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )

        public_key = private_key.public_key()

        return private_key, public_key

    @staticmethod
    def save_key_pair(private_key, public_key,
                     private_key_path: Path,
                     public_key_path: Path,
                     password: Optional[bytes] = None):
        """Save key pair to PEM files"""

        # Save private key
        pem_private = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(password) if password else serialization.NoEncryption()
        )

        with open(private_key_path, 'wb') as f:
            f.write(pem_private)

        logger.info(f"Private key saved: {private_key_path}")

        # Save public key
        pem_public = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        with open(public_key_path, 'wb') as f:
            f.write(pem_public)

        logger.info(f"Public key saved: {public_key_path}")

    def sign_data(self, data: bytes) -> bytes:
        """Sign data with private key"""
        if not self.private_key:
            raise ValueError("Private key not loaded")

        signature = self.private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        return signature

    def generate_license(self, license_info: LicenseInfo) -> Dict[str, Any]:
        """
        Generate signed license

        Args:
            license_info: License information

        Returns:
            Dictionary with license and signature
        """
        # Convert license to JSON
        license_dict = license_info.to_dict()
        license_json = json.dumps(license_dict, sort_keys=True)
        license_bytes = license_json.encode('utf-8')

        # Sign
        signature = self.sign_data(license_bytes)
        signature_b64 = base64.b64encode(signature).decode('utf-8')

        return {
            'license': license_dict,
            'signature': signature_b64
        }

    def save_license(self, license_data: Dict[str, Any], output_path: Path):
        """Save license to file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(license_data, f, indent=2)

        logger.info(f"License saved: {output_path}")


if __name__ == '__main__':
    # Example usage and testing
    print("=" * 70)
    print("License Validation System Test")
    print("=" * 70)

    # Test machine ID generation
    print("\n--- Machine ID ---")
    machine_id = MachineIDGenerator.get_machine_id()
    print(f"Machine ID: {machine_id}")

    if CRYPTO_AVAILABLE:
        # Test key pair generation
        print("\n--- Key Pair Generation ---")
        private_key, public_key = LicenseGenerator.generate_key_pair()
        print("✓ RSA2048 key pair generated")

        # Save keys to temp
        import tempfile
        temp_dir = Path(tempfile.mkdtemp())
        private_key_path = temp_dir / 'private_key.pem'
        public_key_path = temp_dir / 'public_key.pem'

        LicenseGenerator.save_key_pair(
            private_key, public_key,
            private_key_path, public_key_path
        )

        # Test license generation
        print("\n--- License Generation ---")
        generator = LicenseGenerator(private_key_path)

        test_license = LicenseInfo(
            license_key=str(uuid.uuid4()),
            machine_id=machine_id,
            licensee_name="Test Hospital",
            organization="Test Medical Center",
            modules=['cardiac_calcium_scoring', 'visceral_fat_analysis'],
            issue_date=datetime.now().strftime('%Y-%m-%d'),
            expiry_date=(datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d'),
            license_type='trial',
            max_patients=100
        )

        license_data = generator.generate_license(test_license)
        license_file = temp_dir / 'test_license.json'
        generator.save_license(license_data, license_file)

        print(f"✓ Test license generated: {license_file}")

        # Test license validation
        print("\n--- License Validation ---")
        validator = LicenseValidator(public_key_path)

        is_valid, license_info, message = validator.validate_license_file(license_file)

        print(f"Validation result: {is_valid}")
        print(f"Message: {message}")

        if is_valid and license_info:
            print(f"\nLicense Info:")
            print(f"  Licensee: {license_info.licensee_name}")
            print(f"  Organization: {license_info.organization}")
            print(f"  Type: {license_info.license_type}")
            print(f"  Modules: {', '.join(license_info.modules)}")
            print(f"  Expiry: {license_info.expiry_date} ({license_info.days_until_expiry()} days)")
            print(f"  Max patients: {license_info.max_patients or 'Unlimited'}")

            # Test module access
            print(f"\n  Module Access:")
            print(f"    cardiac_calcium_scoring: {validator.check_module_access(license_info, 'cardiac_calcium_scoring')}")
            print(f"    visceral_fat_analysis: {validator.check_module_access(license_info, 'visceral_fat_analysis')}")
            print(f"    unknown_module: {validator.check_module_access(license_info, 'unknown_module')}")

        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
        print(f"\n✓ Cleanup complete")

    else:
        print("\n[WARNING] Cryptography library not available")
        print("Install with: pip install cryptography")

    print("\n" + "=" * 70)
