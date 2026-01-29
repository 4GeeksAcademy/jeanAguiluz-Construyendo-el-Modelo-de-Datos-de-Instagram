from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


# =========================
# TABLA DE ASOCIACIÓN FOLLOWERS
# =========================
class Follower(db.Model):
    __tablename__ = "followers"

    follower_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), primary_key=True
    )
    followed_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), primary_key=True
    )

    # Relaciones explícitas
    follower: Mapped["User"] = relationship(
        "User", foreign_keys=[follower_id], back_populates="following"
    )
    followed: Mapped["User"] = relationship(
        "User", foreign_keys=[followed_id], back_populates="followers"
    )

    def serialize(self):
        return {
            "follower_id": self.follower_id,
            "followed_id": self.followed_id
        }


# =========================
# USERS
# =========================
class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)

    firstname: Mapped[str | None] = mapped_column(String(120))
    lastname: Mapped[str | None] = mapped_column(String(120))
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False)

    # Relaciones
    posts: Mapped[list["Post"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    likes: Mapped[list["Like"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    # Seguidores (usuarios que me siguen)
    followers: Mapped[list["Follower"]] = relationship(
        foreign_keys=[Follower.followed_id],
        back_populates="followed",
        cascade="all, delete-orphan"
    )

    # Seguidos (usuarios que sigo)
    following: Mapped[list["Follower"]] = relationship(
        foreign_keys=[Follower.follower_id],
        back_populates="follower",
        cascade="all, delete-orphan"
    )

    # Perfil 1:1
    profile: Mapped["Profile"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": f"{self.firstname or ''} {self.lastname or ''}".strip(),
            "followers_count": len(self.followers),
            "following_count": len(self.following),
            "post_count": len(self.posts),
        }


# =========================
# POSTS
# =========================
class Post(db.Model):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)

    user: Mapped["User"] = relationship(back_populates="posts")
    likes: Mapped[list["Like"]] = relationship(
        back_populates="post", cascade="all, delete-orphan"
    )

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "image_url": self.image_url
        }


# =========================
# LIKES
# =========================
class Like(db.Model):
    __tablename__ = "likes"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), primary_key=True
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id"), primary_key=True
    )

    user: Mapped["User"] = relationship(back_populates="likes")
    post: Mapped["Post"] = relationship(back_populates="likes")

    def serialize(self):
        return {
            "user_id": self.user_id,
            "post_id": self.post_id
        }


# =========================
# PROFILE (1:1)
# =========================
class Profile(db.Model):
    __tablename__ = "profiles"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), primary_key=True
    )

    bio: Mapped[str | None] = mapped_column(String(150))
    profile_picture_url: Mapped[str | None] = mapped_column(String(500))
    website: Mapped[str | None] = mapped_column(String(200))

    user: Mapped["User"] = relationship(back_populates="profile")

    def serialize(self):
        return {
            "user_id": self.user_id,
            "bio": self.bio,
            "profile_picture_url": self.profile_picture_url,
            "website": self.website
        }
