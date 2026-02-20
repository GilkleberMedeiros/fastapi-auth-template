import unittest
import tempfile
import os
from datetime import datetime, timezone, timedelta
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

from app.utils.jwt import create_token, create_tokens, validate_token, validate_refresh_token


class JWTTestBase(unittest.TestCase):
    """Base class for JWT tests that sets up test keys."""

    @classmethod
    def setUpClass(cls):
        """Generate EC keys for testing."""
        # Generate private key
        private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
        
        # Save private key
        cls.temp_dir = tempfile.mkdtemp()
        cls.priv_key_path = os.path.join(cls.temp_dir, "test_private.pem")
        cls.pub_key_path = os.path.join(cls.temp_dir, "test_public.pem")
        
        with open(cls.priv_key_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Save public key
        public_key = private_key.public_key()
        with open(cls.pub_key_path, "wb") as f:
            f.write(public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))

    @classmethod
    def tearDownClass(cls):
        """Clean up temporary files."""
        if os.path.exists(cls.priv_key_path):
            os.remove(cls.priv_key_path)
        if os.path.exists(cls.pub_key_path):
            os.remove(cls.pub_key_path)
        os.rmdir(cls.temp_dir)


class TestCreateToken(JWTTestBase):
    """Tests for create_token function."""

    def test_create_token_returns_token_data(self):
        """Test that create_token returns a TokenData dict."""
        data = {"id": "user-123"}
        
        token = create_token(
            data, 
            15, 
            "access",
            priv_key_path=self.priv_key_path,
            algorithm="ES256"
        )
        
        self.assertIsInstance(token, dict)
        self.assertIn("token", token)
        self.assertIn("type", token)
        self.assertIn("expires_at", token)

    def test_create_token_has_correct_type(self):
        """Test that create_token sets the correct token type."""
        data = {"id": "user-123"}
        
        token = create_token(
            data, 
            15, 
            "refresh",
            priv_key_path=self.priv_key_path,
            algorithm="ES256"
        )
        
        self.assertEqual(token["type"], "refresh")

    def test_create_token_expires_at_in_future(self):
        """Test that token expiration is in the future."""
        data = {"id": "user-123"}
        before = datetime.now(timezone.utc)
        
        token = create_token(
            data, 
            30, 
            "access",
            priv_key_path=self.priv_key_path,
            algorithm="ES256"
        )
        
        after = datetime.now(timezone.utc)
        
        # expires_at should be around 30 minutes in the future
        self.assertGreater(token["expires_at"], before)
        self.assertLess(token["expires_at"], after + timedelta(minutes=35))

    def test_create_token_with_different_expires_minutes(self):
        """Test token creation with different expiration times."""
        data = {"id": "user-123"}
        
        token_15 = create_token(
            data, 
            15, 
            "access",
            priv_key_path=self.priv_key_path,
            algorithm="ES256"
        )
        
        token_60 = create_token(
            data, 
            60, 
            "access",
            priv_key_path=self.priv_key_path,
            algorithm="ES256"
        )
        
        # 60-minute token should expire later
        self.assertGreater(token_60["expires_at"], token_15["expires_at"])

    def test_create_token_returns_valid_jwt(self):
        """Test that the token can be validated."""
        data = {"id": "user-123"}
        
        token = create_token(
            data, 
            15, 
            "access",
            priv_key_path=self.priv_key_path,
            algorithm="ES256"
        )
        
        # The token should be a valid JWT string
        self.assertIsInstance(token["token"], str)
        self.assertTrue(len(token["token"]) > 0)


class TestCreateTokens(JWTTestBase):
    """Tests for create_tokens function."""

    def test_create_tokens_returns_tokens_data(self):
        """Test that create_tokens returns a TokensData dict."""
        data = {"id": "user-123"}
        
        tokens = create_tokens(
            data,
            priv_key_path=self.priv_key_path,
            access_expires_minutes=15,
            refresh_expires_minutes=2880,
            algorithm="ES256"
        )
        
        self.assertIsInstance(tokens, dict)
        self.assertIn("access_token", tokens)
        self.assertIn("refresh_token", tokens)
        self.assertIn("token_type", tokens)
        self.assertIn("access_expires_at", tokens)
        self.assertIn("refresh_expires_at", tokens)

    def test_create_tokens_has_bearer_type(self):
        """Test that token_type is 'bearer'."""
        data = {"id": "user-123"}
        
        tokens = create_tokens(
            data,
            priv_key_path=self.priv_key_path,
            access_expires_minutes=15,
            refresh_expires_minutes=2880,
            algorithm="ES256"
        )
        
        self.assertEqual(tokens["token_type"], "bearer")

    def test_create_tokens_different_expiration(self):
        """Test that access and refresh tokens have different expiration times."""
        data = {"id": "user-123"}
        
        tokens = create_tokens(
            data,
            priv_key_path=self.priv_key_path,
            access_expires_minutes=15,
            refresh_expires_minutes=2880,
            algorithm="ES256"
        )
        
        # Refresh token should expire much later than access token
        self.assertGreater(tokens["refresh_expires_at"], tokens["access_expires_at"])

    def test_create_tokens_returns_different_tokens(self):
        """Test that access and refresh tokens are different."""
        data = {"id": "user-123"}
        
        tokens = create_tokens(
            data,
            priv_key_path=self.priv_key_path,
            access_expires_minutes=15,
            refresh_expires_minutes=2880,
            algorithm="ES256"
        )
        
        # Tokens should be different
        self.assertNotEqual(tokens["access_token"], tokens["refresh_token"])


class TestValidateToken(JWTTestBase):
    """Tests for validate_token function."""

    def test_validate_token_returns_payload(self):
        """Test that validate_token returns the payload."""
        original_data = {"id": "user-123", "username": "testuser"}
        
        token = create_token(
            original_data,
            15,
            "access",
            priv_key_path=self.priv_key_path,
            algorithm="ES256"
        )
        
        payload = validate_token(
            token["token"],
            pub_key_path=self.pub_key_path,
            algorithm="ES256"
        )
        
        self.assertIsInstance(payload, dict)
        self.assertEqual(payload["id"], original_data["id"])
        self.assertEqual(payload["username"], original_data["username"])

    def test_validate_token_includes_exp(self):
        """Test that payload includes exp claim."""
        original_data = {"id": "user-123"}
        
        token = create_token(
            original_data,
            15,
            "access",
            priv_key_path=self.priv_key_path,
            algorithm="ES256"
        )
        
        payload = validate_token(
            token["token"],
            pub_key_path=self.pub_key_path,
            algorithm="ES256"
        )
        
        self.assertIn("exp", payload)

    def test_validate_invalid_token_raises_error(self):
        """Test that invalid token raises JWTError."""
        from jose import JWTError
        
        with self.assertRaises(JWTError):
            validate_token(
                "invalid.token.here",
                pub_key_path=self.pub_key_path,
                algorithm="ES256"
            )

    def test_validate_token_with_wrong_key_raises_error(self):
        """Test that token signed with different key fails validation."""
        from jose import JWTError
        
        original_data = {"id": "user-123"}
        
        # Create a token with one key pair
        token = create_token(
            original_data,
            15,
            "access",
            priv_key_path=self.priv_key_path,
            algorithm="ES256"
        )
        
        # Generate a different key pair
        different_private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
        different_pub_path = os.path.join(self.temp_dir, "different_pub.pem")
        
        with open(different_pub_path, "wb") as f:
            f.write(different_private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))
        
        try:
            # Try to validate with different public key
            with self.assertRaises(JWTError):
                validate_token(
                    token["token"],
                    pub_key_path=different_pub_path,
                    algorithm="ES256"
                )
        finally:
            if os.path.exists(different_pub_path):
                os.remove(different_pub_path)


class TestValidateRefreshToken(JWTTestBase):
    """Tests for validate_refresh_token function."""

    def test_validate_refresh_token_missing_raises_http_error(self):
        """Test that missing refresh token in cookies raises HTTPException."""
        from fastapi import Request, Response, HTTPException
        from unittest.mock import MagicMock
        
        # Create mock request without refresh_token cookie
        mock_request = MagicMock(spec=Request)
        mock_request.cookies.get.return_value = None
        mock_response = MagicMock(spec=Response)
        
        with self.assertRaises(HTTPException) as context:
            validate_refresh_token(mock_request, mock_response)
        
        self.assertEqual(context.exception.status_code, 400)

    def test_validate_refresh_token_invalid_raises_http_error(self):
        """Test that invalid refresh token raises HTTPException."""
        from fastapi import Request, Response, HTTPException
        from unittest.mock import MagicMock
        
        # Create mock request with invalid token
        mock_request = MagicMock(spec=Request)
        mock_request.cookies.get.return_value = "invalid.token.here"
        mock_response = MagicMock(spec=Response)
        
        with self.assertRaises(HTTPException) as context:
            validate_refresh_token(
                mock_request,
                mock_response,
                pub_key_path=self.pub_key_path,
                algorithm="ES256"
            )
        
        self.assertEqual(context.exception.status_code, 400)

    def test_validate_refresh_token_valid_returns_payload(self):
        """Test that valid refresh token returns payload."""
        from fastapi import Request, Response
        from unittest.mock import MagicMock
        
        original_data = {"id": "user-123"}
        
        # Create a valid token
        token = create_token(
            original_data,
            2880,
            "refresh",
            priv_key_path=self.priv_key_path,
            algorithm="ES256"
        )
        
        # Create mock request with valid token
        mock_request = MagicMock(spec=Request)
        mock_request.cookies.get.return_value = token["token"]
        mock_response = MagicMock(spec=Response)
        
        payload = validate_refresh_token(
            mock_request,
            mock_response,
            pub_key_path=self.pub_key_path,
            algorithm="ES256"
        )
        
        self.assertIsInstance(payload, dict)
        self.assertEqual(payload["id"], original_data["id"])


if __name__ == "__main__":
    unittest.main()
    

