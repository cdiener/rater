create table if not exists persons (
  id integer primary key autoincrement,
  pid integer not null,
  first text not null,
  last text not null,
  email text not null,
  gender text not null,
  birth text not null,
  department text not null,
  institution text not null,
  state text not null,
  country text not null,
  degree text not null,
  profile text not null,
  topic text not null,
  talk_title text,
  talk_abstract text,
  talk_authors text,
  talk_affiliations text,
  poster_title text,
  poster_abstract text,
  poster_authors text,
  poster_affiliations text,
  unique(pid)
);

create table if not exists ratings (
  id integer primary key autoincrement,
  pid integer not null,
  reviewer text not null,
  position integer not null,
  institution integer not null,
  distance integer not null,
  equality integer not null,
  unique(reviewer, pid)
);

create table if not exists abstracts (
  id integer primary key autoincrement,
  pid integer not null,
  reviewer text not null,
  topic integer not null,
  abstract integer not null,
  english integer not null,
  unique(reviewer, pid)
);

insert into persons (pid, first, last, email, gender, birth, department, institution,
    state, country, degree, profile, topic)
    values (1, "Fozzy", "Bear", "fozzy@bear.com", "male", "2000-01-01", "Fun", "Universe",
    "CDMX", "Mexico", "B.Sc.", "bear", "fun fun fun");

insert into persons (pid, first, last, email, gender, birth, department, institution,
    state, country, degree, profile, topic)
    values (2, "Miss", "Piggy", "miss@piggy.com", "female", "2000-01-01","Anger", "MIT",
    "EDOMEX", "Mexico", "M.Sc.", "pig", "love kermit");

insert into persons (pid, first, last, email, gender, birth, department, institution,
    state, country, degree, profile, topic)
    values (3, "Gonzo", "What?", "gonzo@gonzo.com", "male", "2000-01-01","Crazy", "Harvard",
    "New york", "USA", "Ph.D.", "who knows", "cweocjnmnlñmwpq");

insert into persons (pid, first, last, email, gender, birth, department, institution,
    state, country, degree, profile, topic, talk_abstract,
    poster_abstract)
    values (4, "Beaker", "Brrrriii", "beaker@sceince.com", "male", "2000-01-01", "Scientist", "Harvard",
    "New york", "USA", "Ph.D.", "P.I.", "Some sciency stuff",
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec nec dolor urna.
    Integer orci odio, fringilla vel mollis ut, tempus ac sem. Phasellus quis lacinia sapien,
    vitae vulputate diam. Phasellus nisl leo, elementum eget ligula sit amet.",
    "In fringilla tristique viverra. Morbi sit amet cursus lorem. Ut sit amet convallis tellus.
    Mauris aliquam eget leo pellentesque mollis. Proin sit amet mollis erat.
    In hac habitasse platea dictumst."
    );
