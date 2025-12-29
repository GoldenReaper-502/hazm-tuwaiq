"""
HAZM TUWAIQ - Authentication Manager
Handle user authentication, tokens, and sessions
"""

import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
import secrets
import logging

from .models import User, UserLogin, TokenResponse, UserStatus


class AuthManager:
    """
    مدير المصادقة
    Handle authentication and session management
    """
    
    def __init__(self, secret_key: str = None, algorithm: str = "HS256"):
        """
        Initialize authentication manager
        
        Args:
            secret_key: JWT secret key
            algorithm: JWT algorithm
        """
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.algorithm = algorithm
        self.logger = logging.getLogger(__name__)
        
        # Token expiration times
        self.access_token_expire_minutes = 60  # 1 hour
        self.refresh_token_expire_days = 30    # 30 days
        
        # Security settings
        self.max_failed_attempts = 5
        self.lockout_duration_minutes = 30
    
    def hash_password(self, password: str) -> str:
        """
        Hash password using bcrypt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against hash
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password
            
        Returns:
            True if password matches
        """
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            self.logger.error(f"Password verification error: {e}")
            return False
    
    def create_access_token(
        self, 
        user: User,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token
        
        Args:
            user: User object
            expires_delta: Token expiration time
            
        Returns:
            JWT token
        """
        if expires_delta is None:
            expires_delta = timedelta(minutes=self.access_token_expire_minutes)
        
        expire = datetime.utcnow() + expires_delta
        
        payload = {
            "sub": user.id,
            "username": user.username,
            "email": user.email,
            "org_id": user.organization_id,
            "roles": user.roles,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def create_refresh_token(self, user: User) -> str:
        """
        Create JWT refresh token
        
        Args:
            user: User object
            
        Returns:
            JWT refresh token
        """
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        payload = {
            "sub": user.id,
            "org_id": user.organization_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token
            
        Returns:
            Decoded payload or None
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            self.logger.error(f"Invalid token: {e}")
            return None
    
    def authenticate_user(
        self,
        username: str,
        password: str,
        users_db: Dict[str, User]
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        Authenticate user with username and password
        
        Args:
            username: Username
            password: Password
            users_db: Users database
            
        Returns:
            Tuple of (User, error_message)
        """
        # Find user
        user = None
        for u in users_db.values():
            if u.username == username:
                user = u
                break
        
        if not user:
            return None, "المستخدم غير موجود"
        
        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.now():
            remaining = (user.locked_until - datetime.now()).seconds // 60
            return None, f"الحساب مقفل. حاول مرة أخرى بعد {remaining} دقيقة"
        
        # Check if account is active
        if user.status != UserStatus.ACTIVE:
            return None, f"الحساب غير نشط. الحالة: {user.status.value}"
        
        # Verify password
        if not self.verify_password(password, user.password_hash):
            # Increment failed attempts
            user.failed_login_attempts += 1
            
            if user.failed_login_attempts >= self.max_failed_attempts:
                # Lock account
                user.locked_until = datetime.now() + timedelta(
                    minutes=self.lockout_duration_minutes
                )
                return None, f"تم قفل الحساب بسبب محاولات فاشلة متكررة"
            
            remaining = self.max_failed_attempts - user.failed_login_attempts
            return None, f"كلمة مرور خاطئة. محاولات متبقية: {remaining}"
        
        # Reset failed attempts on successful login
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.now()
        
        return user, None
    
    def login(
        self,
        login_data: UserLogin,
        users_db: Dict[str, User]
    ) -> Tuple[Optional[TokenResponse], Optional[str]]:
        """
        Login user and generate tokens
        
        Args:
            login_data: Login request
            users_db: Users database
            
        Returns:
            Tuple of (TokenResponse, error_message)
        """
        # Authenticate
        user, error = self.authenticate_user(
            login_data.username,
            login_data.password,
            users_db
        )
        
        if error:
            return None, error
        
        # Generate tokens
        access_token = self.create_access_token(user)
        refresh_token = self.create_refresh_token(user)
        
        # Update user session
        user.session_token = access_token
        user.refresh_token = refresh_token
        user.token_expires_at = datetime.utcnow() + timedelta(
            minutes=self.access_token_expire_minutes
        )
        user.last_activity = datetime.now()
        
        # Create response
        response = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=self.access_token_expire_minutes * 60,
            user={
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "organization_id": user.organization_id,
                "roles": user.roles,
                "language": user.language
            }
        )
        
        return response, None
    
    def logout(self, user: User):
        """Logout user and clear session"""
        user.session_token = None
        user.refresh_token = None
        user.token_expires_at = None
    
    def refresh_access_token(
        self,
        refresh_token: str,
        users_db: Dict[str, User]
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Refresh token
            users_db: Users database
            
        Returns:
            Tuple of (new_access_token, error_message)
        """
        # Verify refresh token
        payload = self.verify_token(refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            return None, "Refresh token غير صالح"
        
        # Find user
        user_id = payload.get("sub")
        user = users_db.get(user_id)
        
        if not user or user.refresh_token != refresh_token:
            return None, "Refresh token غير صالح"
        
        # Generate new access token
        new_access_token = self.create_access_token(user)
        
        # Update user session
        user.session_token = new_access_token
        user.token_expires_at = datetime.utcnow() + timedelta(
            minutes=self.access_token_expire_minutes
        )
        
        return new_access_token, None


class TokenManager:
    """
    مدير التوكنات
    Manage token lifecycle and validation
    """
    
    def __init__(self, auth_manager: AuthManager):
        """Initialize token manager"""
        self.auth_manager = auth_manager
        self.logger = logging.getLogger(__name__)
    
    def get_current_user(
        self,
        token: str,
        users_db: Dict[str, User]
    ) -> Optional[User]:
        """
        Get current user from token
        
        Args:
            token: JWT token
            users_db: Users database
            
        Returns:
            User or None
        """
        payload = self.auth_manager.verify_token(token)
        
        if not payload:
            return None
        
        user_id = payload.get("sub")
        user = users_db.get(user_id)
        
        if not user or user.session_token != token:
            return None
        
        # Update last activity
        user.last_activity = datetime.now()
        
        return user
    
    def require_auth(
        self,
        token: str,
        users_db: Dict[str, User]
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        Require authentication
        
        Args:
            token: JWT token
            users_db: Users database
            
        Returns:
            Tuple of (User, error_message)
        """
        if not token:
            return None, "Token مطلوب"
        
        user = self.get_current_user(token, users_db)
        
        if not user:
            return None, "Token غير صالح أو منتهي الصلاحية"
        
        if user.status != UserStatus.ACTIVE:
            return None, "الحساب غير نشط"
        
        return user, None


# Singleton instances
_auth_manager: Optional[AuthManager] = None
_token_manager: Optional[TokenManager] = None


def get_auth_manager() -> AuthManager:
    """Get singleton AuthManager instance"""
    global _auth_manager
    
    if _auth_manager is None:
        _auth_manager = AuthManager()
    
    return _auth_manager


def get_token_manager() -> TokenManager:
    """Get singleton TokenManager instance"""
    global _token_manager
    
    if _token_manager is None:
        auth_mgr = get_auth_manager()
        _token_manager = TokenManager(auth_mgr)
    
    return _token_manager
