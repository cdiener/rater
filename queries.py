review_count = 'select count(*) from ratings where reviewer=?'

abstract_rev_count = 'select count(*) from abstracts where reviewer=?'

person_count = 'select count(*) from persons'

next_person = 'select p.pid, p.department, p.institution, p.state, p.country, \
    p.degree, p.profile, p.birth, ifnull(count(r.pid),0) as n, group_concat(r.reviewer) \
    as rev from persons as p left join ratings as r on p.pid=r.pid group by p.pid \
    having instr(rev, ?)=0 or r.reviewer is null order by n limit 1'

next_abstract = 'select p.pid, p.topic, p.abstract_talk, p.abstract_poster, \
    ifnull(count(a.pid),0) as n, group_concat(a.reviewer) as rev \
    from persons as p left join abstracts as a on p.pid=a.pid group by p.pid \
    having instr(rev, ?)=0 or a.reviewer is null order by n limit 1'

insert_person_rating = 'insert or ignore into ratings (pid, reviewer, position, \
    institution, distance, equality) values (?, ?, ?, ?, ?, 0)'

insert_abstract_rating = 'insert or ignore into abstracts (pid, reviewer, topic, \
    abstract, english) values (?, ?, ?, ?, ?)'

average_ratings = 'select pid, avg(position) as p_position, avg(institution) as p_institution, \
    avg(distance) as p_distance, avg(equality) as p_equality, group_concat(reviewer) \
    as reviewers, count(*) as nrev from ratings group by pid'

average_abstracts = 'select pid, avg(topic) as p_topic, avg(abstract) as p_abstract, \
    avg(english) as p_english, group_concat(reviewer) as reviewers, count(*) as nrev \
    from abstracts group by pid'

all_emails = 'select email from persons'
