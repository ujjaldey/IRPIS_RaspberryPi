create table "schedules" (
	"next_schedule_at"	    text not null,
	"duration"	            integer not null default 0,
	"created_at"	        text,
	"updated_at"	        text
);


create table "executions" (
	"id"	                integer unique,
	"executed_at"	        text not null,
	"duration"	            integer not null default 0,
	"type"	                text not null,
	"status"	            text,
	"error"                 text,
	"created_at"	        text,
	"updated_at"	        text,
	primary key("id" AUTOINCREMENT)
);