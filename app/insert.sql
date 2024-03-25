INSERT INTO sample_status (id, name)
VALUES 
  (1, 'Draft'),
  (2, 'Review Pending'),
  (3, 'Requested'),
  (4, 'Received'),
  (5, 'Under Testing'),
  (6, 'Verification Pending'),
  (7, 'Done');

INSERT INTO roles (id, name)
VALUES 
  (1, 'Admin'),
  (2, 'Management'),
  (3, 'QA HOD'),
  (4, 'QA Analyst'),
  (5, 'Marketing Head'),
  (6, 'Marketing Analyst'),
  (7, 'Finance Team'),
  (8, 'Registration Team');

INSERT INTO departments (id, name)
VALUES 
  (1, 'Admin'),
  (2, 'Management'),
  (3, 'QA'),
  (4, 'Marketing'),
  (5, 'Finance'),
  (6, 'Registration');

INSERT INTO menus (id, name)
VALUES 
  (1, 'dashboard'),
  (2, 'customers'),
  (3, 'followup'),
  (4, 'trf'),
  (5, 'registrations'),
  (6, 'samples'),
  (7, 'configurations');

INSERT INTO menu_control_lists (id, menu_id, department_id)
VALUES 
  (1, 1,1),
  (2, 1,2),
  (3, 2,1),
  (4, 2,2),
  (5, 2,4),
  (6, 3,1),
  (7, 3,2),
  (8, 3,4),
  (9, 4,1),
  (10, 4,2),
  (11, 4,4),
  (12, 4,6),
  (13, 5,1),
  (14, 5,2),
  (15, 5,5),
  (16, 5,6),
  (17, 6,1),
  (18, 6,2),
  (19, 6,3),
  (20, 6,5),
  (21, 6,6),
  (22, 7,1);
  