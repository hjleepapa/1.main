-- Create todos_sambanova table
create table public.todos_sambanova (
  id uuid not null default gen_random_uuid (),
  created_at timestamp with time zone not null default now(),
  updated_at timestamp with time zone not null default now(),
  title text not null,
  description text null,
  completed boolean not null default false,
  priority text not null default 'medium'::text,
  due_date timestamp with time zone null,
  google_calendar_event_id text null,
  constraint todos_sambanova_pkey primary key (id)
) TABLESPACE pg_default;

-- Create reminders_sambanova table
create table public.reminders_sambanova (
  id uuid not null default gen_random_uuid (),
  created_at timestamp with time zone not null default now(),
  updated_at timestamp with time zone not null default now(),
  reminder_text text not null,
  importance text not null default 'medium'::text,
  reminder_date timestamp with time zone null,
  google_calendar_event_id text null,
  constraint reminders_sambanova_pkey primary key (id)
) TABLESPACE pg_default;

-- Create calendar_events_sambanova table
create table public.calendar_events_sambanova (
  id uuid not null default gen_random_uuid (),
  created_at timestamp with time zone not null default now(),
  updated_at timestamp with time zone not null default now(),
  title text not null,
  description text null,
  event_from timestamp with time zone not null,
  event_to timestamp with time zone not null,
  google_calendar_event_id text null,
  constraint calendar_events_sambanova_pkey primary key (id)
) TABLESPACE pg_default;

-- Create call_recordings_sambanova table
create table public.call_recordings_sambanova (
  id uuid not null default gen_random_uuid (),
  created_at timestamp with time zone not null default now(),
  call_sid text not null,
  from_number text null,
  to_number text null,
  recording_path text not null,
  duration_seconds integer null,
  file_size_bytes integer null,
  transcription text null,
  status text not null default 'completed'::text,
  constraint call_recordings_sambanova_pkey primary key (id),
  constraint call_recordings_sambanova_call_sid_unique unique (call_sid)
) TABLESPACE pg_default;

-- Create indexes for better performance
create index idx_todos_sambanova_created_at on public.todos_sambanova (created_at);
create index idx_todos_sambanova_completed on public.todos_sambanova (completed);
create index idx_todos_sambanova_priority on public.todos_sambanova (priority);
create index idx_todos_sambanova_due_date on public.todos_sambanova (due_date);

create index idx_reminders_sambanova_created_at on public.reminders_sambanova (created_at);
create index idx_reminders_sambanova_importance on public.reminders_sambanova (importance);
create index idx_reminders_sambanova_reminder_date on public.reminders_sambanova (reminder_date);

create index idx_calendar_events_sambanova_created_at on public.calendar_events_sambanova (created_at);
create index idx_calendar_events_sambanova_event_from on public.calendar_events_sambanova (event_from);
create index idx_calendar_events_sambanova_event_to on public.calendar_events_sambanova (event_to);

create index idx_call_recordings_sambanova_created_at on public.call_recordings_sambanova (created_at);
create index idx_call_recordings_sambanova_call_sid on public.call_recordings_sambanova (call_sid);
create index idx_call_recordings_sambanova_from_number on public.call_recordings_sambanova (from_number);
create index idx_call_recordings_sambanova_status on public.call_recordings_sambanova (status);

-- Add check constraints for valid values
alter table public.todos_sambanova add constraint todos_sambanova_priority_check 
  check (priority in ('low', 'medium', 'high', 'urgent'));

alter table public.reminders_sambanova add constraint reminders_sambanova_importance_check 
  check (importance in ('low', 'medium', 'high', 'urgent'));

-- Add check constraint for event times
alter table public.calendar_events_sambanova add constraint calendar_events_sambanova_time_check 
  check (event_to > event_from);

-- Add check constraints for call recordings
alter table public.call_recordings_sambanova add constraint call_recordings_sambanova_status_check 
  check (status in ('completed', 'failed', 'processing'));

alter table public.call_recordings_sambanova add constraint call_recordings_sambanova_duration_check 
  check (duration_seconds is null or duration_seconds >= 0);

alter table public.call_recordings_sambanova add constraint call_recordings_sambanova_file_size_check 
  check (file_size_bytes is null or file_size_bytes >= 0);
