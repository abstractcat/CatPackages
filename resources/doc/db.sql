CREATE TABLE "public"."account" (
"uname" varchar NOT NULL,
"pwd" varchar,
"status" bool,
CONSTRAINT "account_pkey" PRIMARY KEY ("uname")
)
WITH (OIDS=FALSE)
;

ALTER TABLE "public"."account" OWNER TO "postgres";


CREATE TABLE "public"."entry" (
"uname" varchar NOT NULL,
"address" varchar,
"cookie" text,
CONSTRAINT "cookie_pkey" PRIMARY KEY ("uname")
)
WITH (OIDS=FALSE)
;

ALTER TABLE "public"."entry" OWNER TO "postgres";


CREATE TABLE "public"."proxy" (
"address" varchar NOT NULL,
CONSTRAINT "proxy_pkey" PRIMARY KEY ("address")
)
WITH (OIDS=FALSE)
;

ALTER TABLE "public"."proxy" OWNER TO "postgres";


CREATE TABLE "public"."repost" (
"root_mid" char(16) NOT NULL,
"repost_mid" char(16) NOT NULL,
"uid" char(10),
"uname" varchar,
"content" varchar,
"tm" timestamp(6),
"repost_num" int4,
"comment_num" int4,
"like_num" int4,
CONSTRAINT "repost_pk" PRIMARY KEY ("root_mid", "repost_mid")
)
WITH (OIDS=FALSE)
;

ALTER TABLE "public"."repost" OWNER TO "postgres";


CREATE TABLE "public"."retry" (
"url" varchar NOT NULL,
"type" int2,
CONSTRAINT "retry_pkey" PRIMARY KEY ("url")
)
WITH (OIDS=FALSE)
;

ALTER TABLE "public"."retry" OWNER TO "postgres";


CREATE TABLE "public"."user" (
"uid" char(10) NOT NULL,
"pid" char(16),
"name" varchar,
"follow_num" int4,
"fan_num" int4,
"post_num" int4,
"verify" bool,
CONSTRAINT "user_pkey" PRIMARY KEY ("uid")
)
WITH (OIDS=FALSE)
;

ALTER TABLE "public"."user" OWNER TO "postgres";


CREATE TABLE "public"."weibo" (
"mid" char(16) NOT NULL,
"uid" char(10),
"content" varchar,
"tm" timestamp(6),
"repost_num" int4,
"comment_num" int4,
"like_num" int4,
CONSTRAINT "weibo_pk" PRIMARY KEY ("mid")
)
WITH (OIDS=FALSE)
;

ALTER TABLE "public"."weibo" OWNER TO "postgres";