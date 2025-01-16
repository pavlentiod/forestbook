class AwsTree:
    def __init__(self, root: str, users_path: str, posts_path: str):
        self.root = root
        self.users_path = users_path
        self.posts_path = posts_path

    def user_folder(self, user_id):
        return f"{self.users_path}{user_id}/"

    def post_folder(self, post_id):
        return f"{self.posts_path}{post_id}/"
