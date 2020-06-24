from yoyo import step
steps = [
   step(
       '''
       create table asset(
           id bigserial primary key,
           uploaded_status varchar(255) not null,
           bucket varchar(255) not null,
           object_key varchar(255) not null,
           create_date timestamp not null default now(),
           constraint "bucket_object_key_uq" unique(bucket, object_key)
       )
       ''',
   ),
]