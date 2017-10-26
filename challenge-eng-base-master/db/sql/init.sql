USE challenge;

CREATE TABLE User(id int NOT NULL AUTO_INCREMENT, 
username VARCHAR(20) NOT NULL UNIQUE, password VARCHAR(72) NOT NULL, PRIMARY KEY (id));

CREATE TABLE Message(message_id int NOT NULL AUTO_INCREMENT,
created DATETIME DEFAULT CURRENT_TIMESTAMP, 
sender_id int NOT NULL, receiver_id int NOT NULL, PRIMARY KEY (message_id), 
FOREIGN KEY (sender_id) REFERENCES User(id) ON DELETE CASCADE,
FOREIGN KEY (receiver_id) REFERENCES User(id) ON DELETE CASCADE);

CREATE TABLE Text(message_id int, 
content VARCHAR(150), FOREIGN KEY (message_id) REFERENCES Message (message_id));

CREATE TABLE Image(message_id int, 
image_url VARCHAR(150), height int NOT NULL, width int NOT NULL,
FOREIGN KEY (message_id) REFERENCES Message (message_id));

CREATE TABLE Video(message_id int, 
video_url VARCHAR(150), video_length VARCHAR(20) NOT NULL, video_source VARCHAR(20) NOT NULL,
FOREIGN KEY (message_id) REFERENCES Message (message_id));
