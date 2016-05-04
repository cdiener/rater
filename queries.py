review_count = 'select count(*) from ratings where reviewer=?'

abstract_rev_count = 'select count(*) from abstracts where reviewer=?'

person_count = 'select count(*) from persons'

abstract_count = 'select count(*) from persons where abstract_talk is not null \
    or abstract_poster is not null'

next_person = 'select p.pid, p.department, p.institution, p.state, p.country, \
    p.degree, p.profile, ifnull(count(r.pid),0) as n, group_concat(r.reviewer) \
    as rev from persons as p left join ratings as r on p.pid=r.pid group by p.pid \
    having instr(rev, ?)=0 or r.reviewer is null order by n limit 1'

next_abstract = 'select p.pid, ifnull(count(a.pid),0) as n \
    from persons as p left join abstracts as a on p.pid=a.pid \
    group by p.pid having a.reviewer != "Fozzy" or a.reviewer is null \
    order by n limit 1'

insert_person_rating = 'insert or ignore into ratings (pid, reviewer, position, \
    institution, distance, equality) values (?, ?, ?, ?, ?, 0)'
