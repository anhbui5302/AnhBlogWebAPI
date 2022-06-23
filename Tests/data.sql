INSERT INTO user (name, email, phone, occupation, type)
VALUES
  ('valid_gg_user', 'testgg@gmail.com', '', 'Student', 'Google'),
  ('', 'testgg123@gmail.com', '', '', 'Google'),
  ('valid_fb_user', 'testfb@testing.com', '123456', '', 'Facebook'),
  ('', 'testfb123@gmail.com', '', '', 'Facebook'),
  ('valid_fb_user2', 'testfbyay@abc.com', '', 'Teacher', 'Facebook'),
  ('valid_gg_user2', 'testggyay@xyz.com', '', 'Memer', 'Google');

INSERT INTO post (author_id, created, title, body)
VALUES
  (1, '2022-06-1 00:00:00', 'Post 1', 'Body of post 1'),
  (1, '2022-06-1 00:05:00', 'Post 2', 'Body of post 2'),
  (1, '2022-06-1 00:10:00', 'Post 3', 'Body of post 3'),
  (1, '2022-06-1 00:15:00', 'Post 4', 'Body of post 4'),
  (1, '2022-06-1 00:20:00', 'Post 5', 'Body of post 5'),
  (3, '2022-06-1 01:00:00', 'Post 1', 'Body of post 1'),
  (3, '2022-06-1 01:05:00', 'Post 2', 'Body of post 2'),
  (3, '2022-06-1 01:10:00', 'Post 3', 'Body of post 3'),
  (3, '2022-06-1 01:15:00', 'Post 4', 'Body of post 4'),
  (5, '2022-06-1 02:00:00', 'Post 1', 'Body of post 1'),
  (5, '2022-06-1 02:05:00', 'Post 2', 'Body of post 2'),
  (5, '2022-06-1 02:10:00', 'Post 3', 'Body of post 3'),
  (5, '2022-06-1 02:15:00', 'Post 4', 'Body of post 4'),
  (5, '2022-06-1 02:20:00', 'Post 5', 'Body of post 5'),
  (5, '2022-06-1 02:25:00', 'Post 6', 'Body of post 6'),
  (6, '2022-06-1 03:00:00', 'Post 1', 'Body of post 1'),
  (6, '2022-06-1 03:05:00', 'Post 2', 'Body of post 2'),
  (6, '2022-06-1 03:10:00', 'Post 3', 'Body of post 3');

INSERT INTO like (post_id, user_id, created)
VALUES
  (1, 1, '2022-06-20 00:00:00'),
  (1, 3, '2022-06-20 00:00:00'),
  (1, 5, '2022-06-20 00:00:00'),
  (1, 6, '2022-06-20 00:00:00'),
  (2, 1, '2022-06-20 01:00:00'),
  (2, 3, '2022-06-20 01:00:00'),
  (2, 5, '2022-06-20 01:00:00'),
  (3, 1, '2022-06-20 02:00:00'),
  (3, 3, '2022-06-20 02:00:00'),
  (4, 6, '2022-06-20 03:00:00');