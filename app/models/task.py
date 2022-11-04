from app import db

class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable=True)

    @classmethod
    def to_dict(cls, self):
        return {
            "id": self.task_id,
            "title":self.title,
            "description": self.description,
            "is_complete": True if self.completed_at else False
        }