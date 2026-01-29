from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

class Follower(db.Model):
    __tablename__="followers"
    # Claves foreign y primarias
    follower_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    followed_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    # Relaciones de navegación
    follower: Mapped["User"] = relationship("User", foreign_keys=[follower_id])
    followed: Mapped["User"] = relationship("User", foreign_keys=[followed_id])

    def serialize(self):
        return {
            "follower_id": self.follower_id,
            "followed_id": self.followed_id,
        }


class User(db.Model):
    __tablename__ ="users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    
    # Campos opcionales: Añado firstname y lastname
    firstname: Mapped[str | None] = mapped_column(String(120), nullable=True)
    lastname: Mapped[str | None] = mapped_column (String(120), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False)

    # Relaciones de navegación (one-to-many)
    posts: Mapped[list["Post"]] = relationship(back_populates="user")
    likes: Mapped[list["Like"]] = relationship(back_populates="user")

    # Relación de Seguimiento (Many-to-Many)
    # followers: Mapped[list["Follower"]] = relationship(back_populates="followed_user")
    # followers (seguidores): Los usuarios que me siguen, yo soy followed
    followers: Mapped[list["Follower"]] = relationship(
        secondary="followers", 
        primaryjoin=id == Follower.followed_id, 
        backref="followed_user", 
        lazy=True
    )
    # following (seguidos): usuarios que yo sigo, yo soy el follower
    following: Mapped[list["Follower"]] = relationship(
        secondary="followers",
        primaryjoin=id == Follower.follower_id, 
        backref="follower_user", 
        lazy=True
    )
    
    profile: Mapped["Profile"] = relationship(back_populates="user", lazy=True)


    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": (self.firstname or "") + " " + (self.lastname or ""),
            "post_count": len(self.posts),
            "likes_given_count": len(self.likes),
            "followers_count": len(self.followers),
            "following_count": len(self.following),
            # do not serialize the password, its a security breach
        }

class Post(db.Model):
    __tablename__="posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)

    # Relación de navegación: Post 
    likes: Mapped[list["Like"]] = relationship(back_populates="post", lazy=True)
    # Relación de navegación: 
    user: Mapped["User"] = relationship(back_populates="posts")


    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "image_url": self.image_url,
        }

class Like(db.Model):
    __tablename__="likes"
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey('posts.id'), primary_key=True)

    # Relaciones de navegación
    user: Mapped["User"] = relationship(back_populates="likes")
    post: Mapped["Post"] = relationship(back_populates="likes")

    def serialize(self):
            return {
                "user_id": self.user_id,
                "post_id": self.post_id,
                
        }

class Profile(db.Model):
    __tablename__ = 'profiles'
    
    # Clave Foránea que también es la Clave Primaria (Para forzar 1:1)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
    
    # Atributos específicos del perfil de Instagram
    bio: Mapped[str | None] = mapped_column(String(150), nullable=True)
    profile_picture_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    website: Mapped[str | None] = mapped_column(String(200), nullable=True)
    
    # Relación de navegación: El perfil conoce a su usuario
    user: Mapped["User"] = relationship(back_populates="profile")

    def serialize(self):
        return {
            "user_id": self.user_id,
            "bio": self.bio,
            "profile_picture_url": self.profile_picture_url,
        }
    