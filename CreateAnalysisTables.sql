DROP VIEW IF EXISTS all_data;
CREATE VIEW all_data AS
SELECT *
FROM pPost
JOIN pUser on pUser.id = pPost.userId
JOIN pPostType on pPostType.id = pPost.postTypeCode;


DROP VIEW IF EXISTS tag_data;
create view tag_data as
select tagName, tagDesc, postId, tagId, postId
from pTag
join pPost_pTag on pTag.id = pPost_pTag.tagId;

drop view if exists all_data_tags;
create view all_data_tags as
select * from all_data
join tag_data on tag_data.postId = all_data.id
