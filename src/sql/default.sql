
-- Insert a group
INSERT INTO groups (id, owner_id, name, description)
VALUES (
    'a1b2c3d4-1111-4444-8888-aaaaaaaaaaaa',
    '5e2ab5a6-5601-4b5c-b89c-9aa4054f90af',
    'Nutri group',
    'This is a group for nutrition enthusiasts'
);

-- Insert the user as a member of the group
INSERT INTO group_members (group_id, user_id)
VALUES (
    'a1b2c3d4-1111-4444-8888-aaaaaaaaaaaa',
    '5e2ab5a6-5601-4b5c-b89c-9aa4054f90af'
), (
    'a1b2c3d4-1111-4444-8888-aaaaaaaaaaaa',
    '1a3b5c7d-8901-4e2f-b3c4-1d2e3f4a5b6c'
), (
    'a1b2c3d4-1111-4444-8888-aaaaaaaaaaaa',
    '2b4c6d8e-1234-4f5e-c6d7-2e3f4a5b6c7d'
);

-- Insert a routine for the group
INSERT INTO group_routines (id, group_id, creator_id, name, description, day, start_hour, end_hour)
VALUES (
    'b2c3d4e5-2222-4444-8888-bbbbbbbbbbbb',
    'a1b2c3d4-1111-4444-8888-aaaaaaaaaaaa',
    '5e2ab5a6-5601-4b5c-b89c-9aa4054f90af',
    'Morning Routine',
    'Default morning routine',
    'Monday',
    8,
    10
);

-- Insert an event for the group
INSERT INTO group_events (id, group_id, creator_id, name, description, date, start_hour, end_hour)
VALUES (
    'c3d4e5f6-3333-4444-8888-cccccccccccc',
    'a1b2c3d4-1111-4444-8888-aaaaaaaaaaaa',
    '5e2ab5a6-5601-4b5c-b89c-9aa4054f90af',
    'Kickoff Meeting',
    'Default kickoff event',
    '2025-07-01',
    9,
    11
);

-- Insert a poll for the event
INSERT INTO poll (id, event_id, group_id, creator_id, question)
VALUES (
    'd4e5f6a7-4444-4444-8888-dddddddddddd',
    'c3d4e5f6-3333-4444-8888-cccccccccccc',
    'a1b2c3d4-1111-4444-8888-aaaaaaaaaaaa',
    '5e2ab5a6-5601-4b5c-b89c-9aa4054f90af',
    'What time works best for everyone?'
);

-- Insert poll options
INSERT INTO poll_options (id, poll_id, option_text)
VALUES
    (1, 'd4e5f6a7-4444-4444-8888-dddddddddddd', '9:00 AM'),
    (2, 'd4e5f6a7-4444-4444-8888-dddddddddddd', '10:00 AM'),
    (3, 'd4e5f6a7-4444-4444-8888-dddddddddddd', '11:00 AM');

-- Insert a poll vote for the user
INSERT INTO poll_votes (poll_id, user_id, option_id)
VALUES (
    'd4e5f6a7-4444-4444-8888-dddddddddddd',
    '2b4c6d8e-1234-4f5e-c6d7-2e3f4a5b6c7d',
    1
), (
    'd4e5f6a7-4444-4444-8888-dddddddddddd',
    '1a3b5c7d-8901-4e2f-b3c4-1d2e3f4a5b6c',
    3
);

-- Insert more groups created by different users (owner_id is the user, id is a new group id)
INSERT INTO groups (id, owner_id, name, description)
VALUES
    ('e1f2a3b4-5555-4444-8888-eeeeeeeeeeee', '1a3b5c7d-8901-4e2f-b3c4-1d2e3f4a5b6c', 'Alice Group', 'Group for alice'),
    ('f2a3b4c5-6666-4444-8888-ffffffffffff', '2b4c6d8e-1234-4f5e-c6d7-2e3f4a5b6c7d', 'Bob Group', 'Group for bob'),
    ('a3b4c5d6-7777-4444-8888-aaaaaaaaaaaa', '3c5d7e9f-2345-4g6h-d7e8-3f4a5b6c7d8e', 'Carol Group', 'Group for carol'),
    ('b4c5d6e7-8888-4444-8888-bbbbbbbbbbbb', '4d6e8f0a-3456-4h7i-e8f9-4a5b6c7d8e9f', 'Dave Group', 'Group for dave');

-- Add each owner as a member of their group
INSERT INTO group_members (group_id, user_id) VALUES
    ('e1f2a3b4-5555-4444-8888-eeeeeeeeeeee', '1a3b5c7d-8901-4e2f-b3c4-1d2e3f4a5b6c'),
    ('e1f2a3b4-5555-4444-8888-eeeeeeeeeeee', '5e2ab5a6-5601-4b5c-b89c-9aa4054f90af'),
    ('f2a3b4c5-6666-4444-8888-ffffffffffff', '2b4c6d8e-1234-4f5e-c6d7-2e3f4a5b6c7d'),
    ('f2a3b4c5-6666-4444-8888-ffffffffffff', '5e2ab5a6-5601-4b5c-b89c-9aa4054f90af'),
    ('a3b4c5d6-7777-4444-8888-aaaaaaaaaaaa', '3c5d7e9f-2345-4g6h-d7e8-3f4a5b6c7d8e'),
    ('b4c5d6e7-8888-4444-8888-bbbbbbbbbbbb', '4d6e8f0a-3456-4h7i-e8f9-4a5b6c7d8e9f');


-- -----------

-- Insert a group
INSERT INTO groups (id, owner_id, name, description)
VALUES (
    'b1b2c3d4-1111-4444-8888-aaaaaaaaaaaa',
    '4d6e8f0a-3456-4h7i-e8f9-4a5b6c7d8e9f',
    'Dave nutri group',
    'This is a group for nutrition enthusiasts'
);

-- Insert the user as a member of the group
INSERT INTO group_members (group_id, user_id)
VALUES (
    'b1b2c3d4-1111-4444-8888-aaaaaaaaaaaa',
    '4d6e8f0a-3456-4h7i-e8f9-4a5b6c7d8e9f'
), (
    'b1b2c3d4-1111-4444-8888-aaaaaaaaaaaa',
    '1a3b5c7d-8901-4e2f-b3c4-1d2e3f4a5b6c'
), (
    'b1b2c3d4-1111-4444-8888-aaaaaaaaaaaa',
    '2b4c6d8e-1234-4f5e-c6d7-2e3f4a5b6c7d'
);

-- Insert a routine for the group
INSERT INTO group_routines (id, group_id, creator_id, name, description, day, start_hour, end_hour)
VALUES (
    'c2c3d4e5-2222-4444-8888-bbbbbbbbbbbb',
    'b1b2c3d4-1111-4444-8888-aaaaaaaaaaaa',
    '4d6e8f0a-3456-4h7i-e8f9-4a5b6c7d8e9f',
    'Morning Routine',
    'Default morning routine',
    'Monday',
    8,
    10
);

-- Insert an event for the group
INSERT INTO group_events (id, group_id, creator_id, name, description, date, start_hour, end_hour)
VALUES (
    'h3d4e5f6-3333-4444-8888-cccccccccccc',
    'b1b2c3d4-1111-4444-8888-aaaaaaaaaaaa',
    '4d6e8f0a-3456-4h7i-e8f9-4a5b6c7d8e9f',
    'Kickoff Meeting',
    'Default kickoff event',
    '2025-07-01',
    9,
    11
);

-- Insert a poll for the event
INSERT INTO poll (id, event_id, group_id, creator_id, question)
VALUES (
    'e4e5f6a7-4444-4444-8888-dddddddddddd',
    'h3d4e5f6-3333-4444-8888-cccccccccccc',
    'b1b2c3d4-1111-4444-8888-aaaaaaaaaaaa',
    '4d6e8f0a-3456-4h7i-e8f9-4a5b6c7d8e9f',
    'What time works best for everyone?'
);

-- Insert poll options
INSERT INTO poll_options (id, poll_id, option_text)
VALUES
    (1, 'e4e5f6a7-4444-4444-8888-dddddddddddd', '9:00 AM'),
    (2, 'e4e5f6a7-4444-4444-8888-dddddddddddd', '10:00 AM'),
    (3, 'e4e5f6a7-4444-4444-8888-dddddddddddd', '11:00 AM');

-- Insert a poll vote for the user
INSERT INTO poll_votes (poll_id, user_id, option_id)
VALUES (
    'e4e5f6a7-4444-4444-8888-dddddddddddd',
    '2b4c6d8e-1234-4f5e-c6d7-2e3f4a5b6c7d',
    1
), (
    'e4e5f6a7-4444-4444-8888-dddddddddddd',
    '1a3b5c7d-8901-4e2f-b3c4-1d2e3f4a5b6c',
    3
);

-- Add each owner as a member of their group
INSERT INTO group_members (group_id, user_id) VALUES
    ('e1f2a3b4-5555-4444-8888-eeeeeeeeeeee', '4d6e8f0a-3456-4h7i-e8f9-4a5b6c7d8e9f'),
    ('f2a3b4c5-6666-4444-8888-ffffffffffff', '4d6e8f0a-3456-4h7i-e8f9-4a5b6c7d8e9f');

