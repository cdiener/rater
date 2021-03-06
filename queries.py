review_count = 'select count(*) from ratings where reviewer=?'

abstract_rev_count = 'select count(*) from abstracts where reviewer=?'

abstract_count = 'select count(*) from persons where (talk_abstract is not null or poster_abstract is not null)'

person_count = 'select count(*) from persons'

next_person = 'select p.pid, p.department, p.institution, p.state, p.country, \
    p.degree, p.profile, p.birth, p.topic, ifnull(count(r.pid),0) as n, group_concat(r.reviewer) \
    as rev from persons as p left join ratings as r on p.pid=r.pid group by p.pid \
    having instr(rev, ?)=0 or r.reviewer is null order by n limit 1'

next_abstract = 'select p.pid, p.talk_title, p.talk_authors, p.talk_affiliations, \
    p.talk_abstract, p.poster_title, p.poster_authors, p.poster_affiliations, p.poster_abstract, \
    ifnull(count(a.pid),0) as n, group_concat(a.reviewer) as rev \
    from persons as p left join abstracts as a on p.pid=a.pid group by p.pid \
    having (instr(rev, ?)=0 or a.reviewer is null) and (p.talk_abstract is not null \
    or p.poster_abstract is not null) order by n limit 1'

insert_person_rating = 'insert or replace into ratings (pid, reviewer, position, \
    institution, distance, topic, equality) values (?, ?, ?, ?, ?, ?, 0)'

insert_abstract_rating = 'insert or replace into abstracts (pid, reviewer, \
    abstract, english) values (?, ?, ?, ?)'

average_ratings = 'select pid, avg(position) as p_position, avg(institution) as p_institution, \
    avg(distance) as p_distance, avg(topic) as p_topic, avg(equality) as p_equality, group_concat(reviewer) \
    as reviewers, count(*) as nrev from ratings group by pid'

average_abstracts = 'select pid, avg(abstract) as p_abstract, \
    avg(english) as p_english, group_concat(reviewer) as reviewers, count(*) as nrev \
    from abstracts group by pid'

all_emails = 'select email from persons'

insert_person = 'insert or replace into persons (pid, first, last, email, \
    gender, birth, department, institution, state, country, degree, profile, \
    topic) values (?, ? ,?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'

update_talk = 'update persons set talk_title=?, talk_abstract=?, talk_authors=?, \
    talk_affiliations=? where email=?'

update_poster = 'update persons set poster_title=?, poster_abstract=?, \
    poster_authors=?, poster_affiliations=? where email=?'

insert_complete = 'insert or ignore into persons (pid, first, last, email, \
    gender, birth, department, institution, state, country, degree, profile, \
    topic, talk_title, talk_abstract, talk_authors, talk_affiliations, \
    poster_title, poster_abstract, poster_authors, poster_affiliations) values \
    (?, ? ,?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
