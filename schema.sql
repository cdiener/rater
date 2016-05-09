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
  topic integer not null,
  equality integer not null,
  unique(reviewer, pid)
);

create table if not exists abstracts (
  id integer primary key autoincrement,
  pid integer not null,
  reviewer text not null,
  abstract integer not null,
  english integer not null,
  unique(reviewer, pid)
);
