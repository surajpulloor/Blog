# Blog
A Blog app written in Django

# Requirements
 * Python 3.8+
 * Django 3.2.8+
 * virtualenv (optional)
 * Mysql 8+
 
# Features
 * CRUD on Blogs
 * CRUD on Commens
 * CRUD on Tags
 * Can add multiple tags to a blog
 * User Creation
 * User Auth
 * Like & Dislike Blog
 * Like & Dislike Comment
 * Comments get sorted by their modified timestamp (descending order). Latest comments/replies at the top
 * Give reply to a comment
 * Update/Delete the reply
 * Create a nested comment thread
 * Recover deleted replies if it's reply(child) isn't deleted
 * A user cannot give a reply to his/her comment
 * Pin Comment
 * Page for displaying blog's liked by user (Analytics)
 * Page for displaying blog's disliked by user (Analytics)
 * Page for displaying comments liked by user (Analytics)
 * Page for displaying comments's disliked by user (Analytics)
 * Page for displaying comments's given by user (Analytics)
 * Page for displaying replies given by user (Analytics)
 * Added Rich-Text support to the blog's body. Uses django's quill.js package
 
# TODO
  * Disable the blog's body quill editor
  * Save the images embedded within the quill editor(blog body) on the filesystem, currently being stored in the database along with other text in base64 format.
  * Filter the blogs by month and year