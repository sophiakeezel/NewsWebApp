import unittest
from flasknews import create_app, db
from flasknews.models import User, Post, UserPostAction, Comment

# test database models
class ModelsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # testing user model creation
    def test_user_creation(self):
        user = User(email="test@example.com", username="testuser")
        db.session.add(user)
        db.session.commit()
        self.assertIsNotNone(User.query.filter_by(username='testuser').first())

    # testing post model creation
    def test_post_creation(self):
        post = Post(title="Test Post", content="This is a test post.")
        db.session.add(post)
        db.session.commit()
        retrieved_post = Post.query.filter_by(title="Test Post").first()
        self.assertIsNotNone(retrieved_post)
        self.assertEqual(retrieved_post.content, "This is a test post.")

    # testing user post action model creation
    def test_user_post_action_creation(self):
        user = User(email="testuser@example.com", username="testuser")
        db.session.add(user)
        db.session.commit()

        post = Post(title="Test Post", content="Test content")
        db.session.add(post)
        db.session.commit()

        action = UserPostAction(user_id=user.id,user_name=user.username, post_id=post.id, action='like')
        db.session.add(action)
        db.session.commit()

        retrieved_action = UserPostAction.query.filter_by(user_id=user.id, post_id=post.id).first()
        self.assertIsNotNone(retrieved_action)
        self.assertEqual(retrieved_action.action, 'like')

    # testing comment creation
    def test_comment_creation(self):
        user = User(email="commenter@example.com", username="commenter")
        db.session.add(user)
        db.session.commit()

        comment = Comment(user_id=user.id, username=user.username, text="This is a test comment.")
        db.session.add(comment)
        db.session.commit()

        retrieved_comment = Comment.query.filter_by(user_id=user.id).first()
        self.assertIsNotNone(retrieved_comment)
        self.assertEqual(retrieved_comment.text, "This is a test comment.")

if __name__ == '__main__':
    unittest.main()



