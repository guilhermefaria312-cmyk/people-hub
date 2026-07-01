from __future__ import annotations

import argparse
import hashlib
import json
import re
import secrets
import shutil
import sqlite3
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "data" / "people_hub.local.sqlite"
ADMIN_EMAIL = "guilherme.faria@nvoip.com.br"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(reset: bool = False) -> None:
    with connect() as conn:
        if reset:
            conn.executescript(
                """
                drop table if exists application_comments;
                drop table if exists application_stage_history;
                drop table if exists application_answers;
                drop table if exists applications;
                drop table if exists candidates;
                drop table if exists job_stages;
                drop table if exists job_questions;
                drop table if exists jobs;
                drop table if exists compensation_entries;
                drop table if exists gamification_reward_redemptions;
                drop table if exists gamification_events;
                drop table if exists gamification_badges;
                drop table if exists gamification_rewards;
                drop table if exists gamification_missions;
                drop table if exists gamification_metrics;
                drop table if exists gamification_participants;
                drop table if exists gamification_campaigns;
                drop table if exists pdi_updates;
                drop table if exists pdi_steps;
                drop table if exists pdi_plans;
                drop table if exists career_history;
                drop table if exists career_movements;
                drop table if exists career_development_actions;
                drop table if exists employee_career_reviews;
                drop table if exists employee_career_assignments;
                drop table if exists career_transitions;
                drop table if exists career_role_competencies;
                drop table if exists career_competencies;
                drop table if exists career_roles;
                drop table if exists career_levels;
                drop table if exists career_tracks;
                drop table if exists career_families;
                drop table if exists public_posts;
                drop table if exists time_events;
                drop table if exists users;
                """
            )
        conn.executescript(
            """
            create table if not exists users (
              id integer primary key autoincrement,
              full_name text not null,
              preferred_name text,
              email text not null unique,
              password_hash text,
              role text,
              department text,
              work_mode text,
              hired_at text,
              permission_group text not null default 'Colaborador',
              is_active integer not null default 0,
              must_complete_profile integer not null default 1,
              profile_json text not null default '{}',
              permissions_json text not null default '{}',
              leadership_json text not null default '{}',
              invite_token text,
              invite_expires_at text,
              invite_used_at text,
              created_at text not null,
              updated_at text not null
            );

            create table if not exists public_posts (
              id integer primary key autoincrement,
              author_id integer,
              author_name text not null,
              text text not null,
              reactions_json text not null default '{}',
              created_at text not null,
              updated_at text not null,
              foreign key(author_id) references users(id)
            );

            create table if not exists time_events (
              id integer primary key autoincrement,
              user_id integer,
              user_name text not null,
              event_date text not null,
              event_type text not null,
              title text not null,
              started_at text,
              ended_at text,
              duration_minutes integer not null default 0,
              notes text,
              created_at text not null,
              updated_at text not null,
              foreign key(user_id) references users(id)
            );

            create table if not exists compensation_entries (
              id integer primary key autoincrement,
              user_id integer,
              user_name text not null,
              competence text not null,
              salary_base real not null default 0,
              commission real not null default 0,
              bonus real not null default 0,
              plr real not null default 0,
              va real not null default 0,
              vr real not null default 0,
              vt real not null default 0,
              cost_allowance real not null default 0,
              reimbursements real not null default 0,
              dailies real not null default 0,
              discounts real not null default 0,
              status text not null default 'Rascunho',
              notes text,
              created_at text not null,
              updated_at text not null,
              foreign key(user_id) references users(id)
            );

            create table if not exists gamification_campaigns (
              id integer primary key autoincrement,
              name text not null,
              description text,
              objective text,
              theme text not null default 'Missão corporativa',
              campaign_type text not null default 'Missões individuais',
              status text not null default 'Rascunho',
              start_date text,
              end_date text,
              visibility text not null default 'Participantes',
              created_by integer,
              created_by_name text,
              department_scope text,
              participation_mode text not null default 'Individual',
              scoring_mode text not null default 'Manual',
              leaderboard_type text not null default 'Ranking competitivo',
              reward_policy text,
              healthy_mode integer not null default 1,
              score_weights_json text not null default '{}',
              rules_summary text,
              settings_json text not null default '{}',
              created_at text not null,
              updated_at text not null,
              foreign key(created_by) references users(id)
            );

            create table if not exists gamification_participants (
              id integer primary key autoincrement,
              campaign_id integer not null,
              user_id integer,
              user_name text not null,
              team_name text,
              current_points integer not null default 0,
              current_level text not null default 'Nível 1',
              current_rank integer not null default 0,
              badges_json text not null default '[]',
              coins integer not null default 0,
              status text not null default 'Ativo',
              joined_at text not null,
              updated_at text not null,
              foreign key(campaign_id) references gamification_campaigns(id) on delete cascade,
              foreign key(user_id) references users(id)
            );

            create table if not exists gamification_metrics (
              id integer primary key autoincrement,
              campaign_id integer not null,
              name text not null,
              description text,
              score_type text not null default 'Resultado',
              source_type text not null default 'Manual',
              source_config text not null default '{}',
              points integer not null default 0,
              negative_points integer not null default 0,
              weight real not null default 1,
              max_points_per_day integer,
              max_points_per_week integer,
              approval_required integer not null default 0,
              tiebreaker text,
              multiplier real not null default 1,
              recurrence text,
              active integer not null default 1,
              created_at text not null,
              updated_at text not null,
              foreign key(campaign_id) references gamification_campaigns(id) on delete cascade
            );

            create table if not exists gamification_missions (
              id integer primary key autoincrement,
              campaign_id integer not null,
              title text not null,
              description text,
              points integer not null default 0,
              deadline text,
              mission_type text not null default 'Individual',
              completion_type text not null default 'Evidência',
              approval_required integer not null default 0,
              evidence_required integer not null default 0,
              required integer not null default 0,
              unlock_badge text,
              unlock_reward_id integer,
              phase_name text,
              active integer not null default 1,
              created_at text not null,
              updated_at text not null,
              foreign key(campaign_id) references gamification_campaigns(id) on delete cascade
            );

            create table if not exists gamification_rewards (
              id integer primary key autoincrement,
              campaign_id integer,
              name text not null,
              description text,
              reward_type text not null default 'Simbólica',
              cost_in_coins integer not null default 0,
              stock integer,
              image_url text,
              approval_required integer not null default 0,
              valid_until text,
              eligibility_rules text,
              active integer not null default 1,
              created_at text not null,
              updated_at text not null,
              foreign key(campaign_id) references gamification_campaigns(id) on delete cascade
            );

            create table if not exists gamification_badges (
              id integer primary key autoincrement,
              campaign_id integer,
              name text not null,
              description text,
              icon text,
              trigger_rule text,
              active integer not null default 1,
              created_at text not null,
              updated_at text not null,
              foreign key(campaign_id) references gamification_campaigns(id) on delete cascade
            );

            create table if not exists gamification_events (
              id integer primary key autoincrement,
              campaign_id integer not null,
              participant_id integer,
              metric_id integer,
              mission_id integer,
              event_type text not null default 'Pontuação manual',
              points integer not null default 0,
              coins integer not null default 0,
              source text not null default 'Manual',
              evidence_url text,
              justification text,
              status text not null default 'Aprovado',
              approved_by integer,
              approved_by_name text,
              created_by integer,
              created_by_name text,
              created_at text not null,
              foreign key(campaign_id) references gamification_campaigns(id) on delete cascade,
              foreign key(participant_id) references gamification_participants(id) on delete cascade,
              foreign key(metric_id) references gamification_metrics(id),
              foreign key(mission_id) references gamification_missions(id)
            );

            create table if not exists gamification_reward_redemptions (
              id integer primary key autoincrement,
              reward_id integer not null,
              campaign_id integer,
              participant_id integer,
              cost_in_coins integer not null default 0,
              status text not null default 'Solicitado',
              requested_at text not null,
              approved_by integer,
              approved_at text,
              notes text,
              foreign key(reward_id) references gamification_rewards(id),
              foreign key(campaign_id) references gamification_campaigns(id) on delete cascade,
              foreign key(participant_id) references gamification_participants(id)
            );

            create table if not exists pdi_plans (
              id integer primary key autoincrement,
              employee_id integer not null,
              employee_name text not null,
              manager_id integer,
              manager_name text,
              title text not null,
              pdi_type text not null default 'Desenvolvimento',
              status text not null default 'Aberto',
              urgency text not null default 'Médio',
              progress integer not null default 0,
              current_role text,
              team text,
              current_level text,
              main_responsibilities text,
              current_moment text,
              strengths text,
              strengths_description text,
              gaps text,
              improvements text,
              evidences text,
              recognition text,
              feedback_reaction text,
              expected_change text,
              impact_area text,
              learning_profile text,
              learning_method text,
              resources text,
              followup_frequency text,
              expected_term text,
              main_metric text,
              due_date text,
              objective text,
              diagnosis text,
              success_criteria text,
              structured_json text not null default '{}',
              final_evaluation text,
              created_at text not null,
              updated_at text not null,
              foreign key(employee_id) references users(id),
              foreign key(manager_id) references users(id)
            );

            create table if not exists pdi_steps (
              id integer primary key autoincrement,
              plan_id integer not null,
              period text not null,
              title text not null,
              description text,
              expected_evidence text,
              due_date text,
              status text not null default 'Pendente',
              progress integer not null default 0,
              evidence text,
              employee_comment text,
              manager_comment text,
              completed_at text,
              created_at text not null,
              updated_at text not null,
              foreign key(plan_id) references pdi_plans(id) on delete cascade
            );

            create table if not exists pdi_updates (
              id integer primary key autoincrement,
              plan_id integer not null,
              step_id integer,
              author_id integer,
              author_name text not null,
              author_role text,
              update_type text not null default 'Comentário',
              comment text,
              evidence text,
              progress integer,
              created_at text not null,
              foreign key(plan_id) references pdi_plans(id) on delete cascade,
              foreign key(step_id) references pdi_steps(id) on delete cascade
            );

            create table if not exists career_families (
              id integer primary key autoincrement,
              name text not null,
              description text,
              owner_id integer,
              status text not null default 'Ativa',
              created_at text not null,
              updated_at text not null,
              foreign key(owner_id) references users(id)
            );

            create table if not exists career_tracks (
              id integer primary key autoincrement,
              family_id integer,
              name text not null,
              description text,
              type text not null default 'Técnica',
              display_order integer not null default 0,
              status text not null default 'Ativa',
              created_at text not null,
              updated_at text not null,
              foreign key(family_id) references career_families(id)
            );

            create table if not exists career_levels (
              id integer primary key autoincrement,
              name text not null,
              description text,
              hierarchy_order integer not null default 0,
              seniority_weight integer not null default 0,
              status text not null default 'Ativo',
              created_at text not null,
              updated_at text not null
            );

            create table if not exists career_roles (
              id integer primary key autoincrement,
              family_id integer,
              track_id integer,
              level_id integer,
              name text not null,
              mission text,
              description text,
              responsibilities text,
              expected_deliverables text,
              required_requirements text,
              desired_requirements text,
              recommended_courses text,
              min_time_months integer not null default 0,
              salary_min real,
              salary_mid real,
              salary_max real,
              salary_visibility text not null default 'Restrita',
              bonus_eligible integer not null default 0,
              commission_eligible integer not null default 0,
              status text not null default 'Ativo',
              created_at text not null,
              updated_at text not null,
              foreign key(family_id) references career_families(id),
              foreign key(track_id) references career_tracks(id),
              foreign key(level_id) references career_levels(id)
            );

            create table if not exists career_competencies (
              id integer primary key autoincrement,
              name text not null,
              type text not null default 'Comportamental',
              description text,
              behavior_examples text,
              status text not null default 'Ativa',
              created_at text not null,
              updated_at text not null
            );

            create table if not exists career_role_competencies (
              id integer primary key autoincrement,
              role_id integer not null,
              competency_id integer not null,
              expected_level text not null default 'Intermediário',
              weight integer not null default 1,
              required integer not null default 1,
              role_specific_description text,
              created_at text not null,
              updated_at text not null,
              foreign key(role_id) references career_roles(id),
              foreign key(competency_id) references career_competencies(id)
            );

            create table if not exists career_transitions (
              id integer primary key autoincrement,
              from_role_id integer,
              to_role_id integer,
              transition_type text not null default 'Promoção',
              min_time_months integer not null default 0,
              required_performance_score real,
              required_360_score real,
              requires_pdi_completed integer not null default 0,
              requires_manager_approval integer not null default 1,
              requires_hr_approval integer not null default 1,
              requires_director_approval integer not null default 0,
              criteria_description text,
              status text not null default 'Ativa',
              created_at text not null,
              updated_at text not null,
              foreign key(from_role_id) references career_roles(id),
              foreign key(to_role_id) references career_roles(id)
            );

            create table if not exists employee_career_assignments (
              id integer primary key autoincrement,
              employee_id integer not null,
              family_id integer,
              track_id integer,
              role_id integer,
              level_id integer,
              manager_id integer,
              started_at text,
              last_movement_at text,
              suggested_next_role_id integer,
              career_status text not null default 'Sem plano definido',
              hr_notes text,
              manager_notes text,
              visible_to_employee integer not null default 1,
              created_at text not null,
              updated_at text not null,
              foreign key(employee_id) references users(id)
            );

            create table if not exists employee_career_reviews (
              id integer primary key autoincrement,
              employee_id integer not null,
              current_role_id integer,
              target_role_id integer,
              reviewer_id integer,
              review_type text,
              criteria_snapshot text not null default '{}',
              readiness_score integer not null default 0,
              status text not null default 'Não avaliado',
              comments text,
              created_at text not null,
              updated_at text not null
            );

            create table if not exists career_development_actions (
              id integer primary key autoincrement,
              employee_id integer not null,
              competency_id integer,
              role_id integer,
              target_role_id integer,
              pdi_action_id integer,
              title text not null,
              description text,
              due_date text,
              status text not null default 'Aberta',
              created_at text not null,
              updated_at text not null
            );

            create table if not exists career_movements (
              id integer primary key autoincrement,
              employee_id integer not null,
              from_role_id integer,
              to_role_id integer,
              requested_by integer,
              movement_type text not null default 'Promoção',
              reason text,
              status text not null default 'Em análise pelo RH',
              effective_date text,
              approved_by_manager_id integer,
              approved_by_hr_id integer,
              approved_by_director_id integer,
              rejection_reason text,
              created_at text not null,
              updated_at text not null
            );

            create table if not exists career_history (
              id integer primary key autoincrement,
              employee_id integer not null,
              event_type text not null,
              from_role_id integer,
              to_role_id integer,
              description text,
              event_date text,
              created_by integer,
              created_at text not null
            );

            create table if not exists jobs (
              id integer primary key autoincrement,
              title text not null,
              department text,
              level text,
              quantity integer not null default 1,
              contract_type text,
              work_model text,
              city text,
              work_location text,
              journey text,
              working_hours text,
              salary_min real,
              salary_max real,
              salary_text text,
              show_salary integer not null default 0,
              benefits_json text not null default '[]',
              additional_benefits text,
              summary text,
              responsibilities text,
              required_requirements text,
              desired_requirements text,
              education_level text,
              experience_level text,
              behavioral_profile text,
              internal_notes text,
              responsible_user_id integer,
              responsible_name text,
              deadline text,
              status text not null default 'Rascunho',
              slug text not null unique,
              published_at text,
              created_at text not null,
              updated_at text not null,
              foreign key(responsible_user_id) references users(id)
            );

            create table if not exists job_questions (
              id integer primary key autoincrement,
              job_id integer not null,
              question text not null,
              answer_type text not null default 'Texto curto',
              options_json text not null default '[]',
              required integer not null default 0,
              knockout integer not null default 0,
              expected_answer text,
              weight integer not null default 1,
              sort_order integer not null default 0,
              created_at text not null,
              foreign key(job_id) references jobs(id)
            );

            create table if not exists job_stages (
              id integer primary key autoincrement,
              job_id integer not null,
              name text not null,
              sort_order integer not null default 0,
              color text,
              type text not null default 'Intermediária',
              active integer not null default 1,
              created_at text not null,
              foreign key(job_id) references jobs(id)
            );

            create table if not exists candidates (
              id integer primary key autoincrement,
              full_name text not null,
              email text not null,
              whatsapp text,
              city text,
              state text,
              neighborhood text,
              linkedin_url text,
              portfolio_url text,
              resume_url text,
              education_level text,
              course text,
              experience_level text,
              experience_summary text,
              currently_working text,
              talent_pool_accepted integer not null default 0,
              lgpd_accepted integer not null default 0,
              created_at text not null,
              updated_at text not null
            );

            create table if not exists applications (
              id integer primary key autoincrement,
              job_id integer not null,
              candidate_id integer not null,
              current_stage_id integer,
              salary_expectation real,
              availability_start text,
              availability_schedule text,
              accepts_work_model text,
              source text not null default 'Página pública',
              ats_score integer not null default 0,
              ats_classification text,
              ats_summary text,
              ats_strengths text,
              ats_risks text,
              ats_recommendation text,
              status text not null default 'Em aberto',
              favorite integer not null default 0,
              created_at text not null,
              updated_at text not null,
              foreign key(job_id) references jobs(id),
              foreign key(candidate_id) references candidates(id),
              foreign key(current_stage_id) references job_stages(id)
            );

            create table if not exists application_answers (
              id integer primary key autoincrement,
              application_id integer not null,
              question_id integer,
              question text not null,
              answer text,
              knockout_passed integer,
              created_at text not null,
              foreign key(application_id) references applications(id),
              foreign key(question_id) references job_questions(id)
            );

            create table if not exists application_stage_history (
              id integer primary key autoincrement,
              application_id integer not null,
              from_stage_id integer,
              to_stage_id integer,
              moved_by_user_id integer,
              comment text,
              created_at text not null,
              foreign key(application_id) references applications(id)
            );

            create table if not exists application_comments (
              id integer primary key autoincrement,
              application_id integer not null,
              user_id integer,
              comment text not null,
              created_at text not null,
              foreign key(application_id) references applications(id)
            );
            """
        )
        admin = conn.execute("select id from users where lower(email) = ?", (ADMIN_EMAIL,)).fetchone()
        now = iso(utc_now())
        if not admin:
            conn.execute(
                """
                insert into users (
                  full_name, preferred_name, email, password_hash, role, department,
                  work_mode, hired_at, permission_group, is_active,
                  must_complete_profile, profile_json, permissions_json, leadership_json,
                  created_at, updated_at
                ) values (?, ?, ?, null, ?, ?, ?, ?, ?, 1, 0, ?, ?, ?, ?, ?)
                """,
                (
                    "Guilherme Faria",
                    "Guilherme",
                    ADMIN_EMAIL,
                    "Administrador",
                    "Diretoria",
                    "Híbrido",
                    "",
                    "Admin",
                    json.dumps({"nickname": "Guilherme"}, ensure_ascii=False),
                    json.dumps(default_permissions("Admin"), ensure_ascii=False),
                    json.dumps({}, ensure_ascii=False),
                    now,
                    now,
                ),
            )


def default_permissions(group: str) -> dict[str, bool]:
    presets = {
        "Colaborador": ["peopleHub"],
        "Líder": ["peopleHub", "leaderData"],
        "RH": ["peopleHub", "hrDp", "manageUsers"],
        "Líder de RH": ["peopleHub", "leaderData", "hrDp", "manageUsers", "payroll"],
        "Diretor": ["peopleHub", "leaderData", "directorData"],
        "Admin": ["peopleHub", "leaderData", "directorData", "hrDp", "manageUsers", "payroll", "financials", "admin"],
    }
    keys = ["peopleHub", "leaderData", "directorData", "hrDp", "manageUsers", "payroll", "financials", "admin"]
    allowed = set(presets.get(group, presets["Colaborador"]))
    return {key: key in allowed for key in keys}


def public_user(row: sqlite3.Row) -> dict:
    profile = json.loads(row["profile_json"] or "{}")
    permissions = json.loads(row["permissions_json"] or "{}")
    leadership = json.loads(row["leadership_json"] or "{}")
    invite_expires_at = row["invite_expires_at"]
    invite_status = "sem link"
    if row["invite_token"] and not row["invite_used_at"]:
        try:
            expires = datetime.fromisoformat(invite_expires_at)
            invite_status = "expirado" if expires < utc_now() else "válido"
        except (TypeError, ValueError):
            invite_status = "expirado"
    elif row["invite_used_at"]:
        invite_status = "usado"

    return {
        "id": row["id"],
        "full_name": row["full_name"],
        "preferred_name": row["preferred_name"],
        "email": row["email"],
        "role": row["role"],
        "department": row["department"],
        "work_mode": row["work_mode"],
        "hired_at": row["hired_at"],
        "permission_group": row["permission_group"],
        "is_active": bool(row["is_active"]),
        "must_complete_profile": bool(row["must_complete_profile"]),
        "profile": profile,
        "permissions": permissions,
        "leadership": leadership,
        "invite_token": row["invite_token"],
        "invite_expires_at": invite_expires_at,
        "invite_status": invite_status,
        "invite_link": f"http://localhost:5173/convite/{row['invite_token']}" if row["invite_token"] else "",
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def public_post(row: sqlite3.Row) -> dict:
    reactions = json.loads(row["reactions_json"] or "{}")
    return {
        "id": row["id"],
        "author_id": row["author_id"],
        "author_name": row["author_name"],
        "text": row["text"],
        "reactions": reactions,
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def public_time_event(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "user_name": row["user_name"],
        "event_date": row["event_date"],
        "event_type": row["event_type"],
        "title": row["title"],
        "started_at": row["started_at"],
        "ended_at": row["ended_at"],
        "duration_minutes": row["duration_minutes"],
        "notes": row["notes"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def public_compensation(row: sqlite3.Row) -> dict:
    values = {
        "salary_base": row["salary_base"],
        "commission": row["commission"],
        "bonus": row["bonus"],
        "plr": row["plr"],
        "va": row["va"],
        "vr": row["vr"],
        "vt": row["vt"],
        "cost_allowance": row["cost_allowance"],
        "reimbursements": row["reimbursements"],
        "dailies": row["dailies"],
        "discounts": row["discounts"],
    }
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "user_name": row["user_name"],
        "competence": row["competence"],
        **values,
        "gross_total": sum(float(values[key] or 0) for key in values if key != "discounts"),
        "net_projection": sum(float(values[key] or 0) for key in values if key != "discounts") - float(values["discounts"] or 0),
        "status": row["status"],
        "notes": row["notes"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def public_gamification_row(row: sqlite3.Row) -> dict:
    data = row_dict(row)
    for key in ("healthy_mode", "approval_required", "evidence_required", "required", "active"):
        if key in data:
            data[key] = bool(data[key])
    for key in ("score_weights_json", "settings_json", "badges_json", "source_config"):
        if key in data:
            target = key.replace("_json", "")
            try:
                data[target] = json.loads(data.pop(key) or ("[]" if key == "badges_json" else "{}"))
            except json.JSONDecodeError:
                data[target] = [] if key == "badges_json" else {}
    return data


def gamification_theme_meta(theme: str) -> dict:
    themes = {
        "Copa do Mundo": {"accent": "#2f7a55", "level_names": ["Torcida", "Titular", "Craque", "Capitão"], "banner": "Estádio interno em clima de campanha"},
        "Corrida espacial": {"accent": "#4b6f9f", "level_names": ["Tripulação", "Órbita", "Comando", "Missão Alfa"], "banner": "Jornada espacial rumo à meta"},
        "Montanha": {"accent": "#2f6f73", "level_names": ["Base", "Trilha", "Cume", "Expedição"], "banner": "Subida progressiva com marcos claros"},
        "Fórmula 1": {"accent": "#b84a62", "level_names": ["Grid", "Box", "Pódio", "Pole"], "banner": "Ritmo, qualidade e ultrapassagens saudáveis"},
        "RPG medieval": {"accent": "#6e5d94", "level_names": ["Aprendiz", "Guardião", "Mestre", "Lenda"], "banner": "Jornada por fases e conquistas"},
        "Ilha do tesouro": {"accent": "#a66a3f", "level_names": ["Mapa", "Rota", "Tesouro", "Conquista"], "banner": "Missões, pistas e recompensas"},
        "Liga dos campeões": {"accent": "#4f8f71", "level_names": ["Grupo", "Oitavas", "Final", "Campeão"], "banner": "Temporada com fases e ranking"},
        "Missão corporativa": {"accent": "#632947", "level_names": ["Início", "Tração", "Impacto", "Referência"], "banner": "Campanha institucional com impacto real"},
        "Operação resgate": {"accent": "#2f7a55", "level_names": ["Alerta", "Ação", "Virada", "Resgate"], "banner": "Meta coletiva para recuperar indicadores"},
        "Batalha dos KPIs": {"accent": "#f37435", "level_names": ["Sinal", "Ritmo", "Meta", "Excelência"], "banner": "Indicadores em disputa saudável"},
    }
    return themes.get(theme or "", themes["Missão corporativa"])


def refresh_gamification_ranking(conn: sqlite3.Connection, campaign_id: int) -> None:
    rows = conn.execute(
        """
        select p.id,
               coalesce(sum(case when e.status = 'Aprovado' then e.points else 0 end), 0) as points,
               coalesce(sum(case when e.status = 'Aprovado' then e.coins else 0 end), 0) as coins
        from gamification_participants p
        left join gamification_events e on e.participant_id = p.id
        where p.campaign_id = ?
        group by p.id
        order by points desc, coins desc, p.id asc
        """,
        (campaign_id,),
    ).fetchall()
    now = iso(utc_now())
    theme = conn.execute("select theme from gamification_campaigns where id = ?", (campaign_id,)).fetchone()
    levels = gamification_theme_meta(theme["theme"] if theme else "")["level_names"]
    for index, row in enumerate(rows, start=1):
        points = int(row["points"] or 0)
        if points >= 900:
            level = levels[-1]
        elif points >= 500:
            level = levels[min(2, len(levels) - 1)]
        elif points >= 150:
            level = levels[min(1, len(levels) - 1)]
        else:
            level = levels[0]
        conn.execute(
            """
            update gamification_participants
            set current_points = ?, coins = ?, current_rank = ?, current_level = ?, updated_at = ?
            where id = ?
            """,
            (points, int(row["coins"] or 0), index, level, now, row["id"]),
        )


def gamification_payload(conn: sqlite3.Connection, user_id: str = "") -> dict:
    campaign_rows = conn.execute("select * from gamification_campaigns order by created_at desc, id desc").fetchall()
    campaigns = [public_gamification_row(row) for row in campaign_rows]
    for campaign in campaigns:
        refresh_gamification_ranking(conn, int(campaign["id"]))
    participants = [public_gamification_row(row) for row in conn.execute("select * from gamification_participants order by campaign_id asc, current_rank asc, user_name asc").fetchall()]
    metrics = [public_gamification_row(row) for row in conn.execute("select * from gamification_metrics order by campaign_id asc, id asc").fetchall()]
    missions = [public_gamification_row(row) for row in conn.execute("select * from gamification_missions order by campaign_id asc, deadline asc, id asc").fetchall()]
    rewards = [public_gamification_row(row) for row in conn.execute("select * from gamification_rewards order by active desc, cost_in_coins asc, name asc").fetchall()]
    badges = [public_gamification_row(row) for row in conn.execute("select * from gamification_badges order by campaign_id asc, name asc").fetchall()]
    events = [public_gamification_row(row) for row in conn.execute("select * from gamification_events order by created_at desc, id desc limit 250").fetchall()]
    redemptions = [public_gamification_row(row) for row in conn.execute("select * from gamification_reward_redemptions order by requested_at desc, id desc").fetchall()]
    campaign_ids_for_user = set()
    if user_id:
        campaign_ids_for_user = {item["campaign_id"] for item in participants if str(item.get("user_id")) == str(user_id)}
    active_campaigns = [item for item in campaigns if item["status"] == "Publicada"]
    participant_users = {item.get("user_id") for item in participants if item.get("user_id")}
    engaged_users = {event.get("participant_id") for event in events if event.get("status") == "Aprovado"}
    summary = {
        "active_campaigns": len(active_campaigns),
        "finished_campaigns": len([item for item in campaigns if item["status"] == "Finalizada"]),
        "participants": len(participants),
        "inactive_participants": len([item for item in participants if item["status"] != "Ativo"]),
        "points_distributed": sum(int(item.get("points") or 0) for item in events if item.get("status") == "Aprovado"),
        "rewards_redeemed": len(redemptions),
        "engagement_rate": round((len(engaged_users) / len(participants)) * 100) if participants else 0,
        "participant_users": len(participant_users),
    }
    insights = []
    if not campaigns:
        insights.append("Nenhuma campanha criada ainda. Use templates para iniciar uma campanha manual, automática ou híbrida.")
    if active_campaigns and summary["engagement_rate"] < 50:
        insights.append("Há campanha ativa com adesão baixa. Considere missão simples de entrada ou comunicação no mural.")
    if metrics and not any(metric.get("score_type") == "Qualidade" for metric in metrics):
        insights.append("As regras atuais ainda não possuem indicador de qualidade. O modo saudável recomenda equilibrar volume e qualidade.")
    if events and any(event.get("source") == "Manual" and not event.get("justification") for event in events):
        insights.append("Existem pontuações manuais sem justificativa. A auditoria deve exigir contexto para evitar distorções.")
    return {
        "campaigns": campaigns,
        "participants": participants,
        "metrics": metrics,
        "missions": missions,
        "rewards": rewards,
        "badges": badges,
        "events": events,
        "redemptions": redemptions,
        "summary": summary,
        "insights": insights,
        "my_campaign_ids": list(campaign_ids_for_user),
    }


def pdi_status_from_progress(progress: int, due_date: str | None, requested_status: str = "") -> str:
    if requested_status in ("Pausado", "Cancelado"):
        return requested_status
    if progress >= 100:
        return "Concluído"
    if due_date:
        try:
            if datetime.fromisoformat(due_date).date() < utc_now().date():
                return "Atrasado"
        except ValueError:
            pass
    if progress > 0:
        return "Em andamento"
    return requested_status or "Aberto"


def pdi_quality(plan: dict, steps: list[dict], updates: list[dict]) -> dict:
    progress = int(plan.get("progress") or 0)
    urgency = plan.get("urgency") or "Médio"
    overdue = plan.get("status") == "Atrasado"
    evidence_count = len([item for item in steps + updates if item.get("evidence")])
    completed_steps = len([item for item in steps if item.get("status") == "Concluído"])
    if progress >= 100:
        return {
            "label": "Concluído",
            "message": "PDI concluído. O próximo passo é validar se a evolução apareceu nas métricas e comportamentos observáveis.",
        }
    if overdue or (urgency == "Alto" and progress < 30):
        return {
            "label": "Crítico",
            "message": "PDI crítico. Prazo, urgência ou baixa execução pedem acompanhamento mais próximo do gestor e RH.",
        }
    if progress >= 50 and evidence_count and completed_steps:
        return {
            "label": "Em boa evolução",
            "message": "PDI em boa evolução. Há passos concluídos e evidências registradas para sustentar a mudança.",
        }
    return {
        "label": "Atenção",
        "message": "PDI exige atenção. Há plano estruturado, mas ainda faltam evidências objetivas ou mais execução registrada.",
    }


def public_pdi_plan(row: sqlite3.Row) -> dict:
    data = row_dict(row)
    try:
        data["structured"] = json.loads(data.pop("structured_json") or "{}")
    except json.JSONDecodeError:
        data["structured"] = {}
    return data


def public_pdi_step(row: sqlite3.Row) -> dict:
    return row_dict(row)


def public_pdi_update(row: sqlite3.Row) -> dict:
    return row_dict(row)


def pdi_payload(conn: sqlite3.Connection, employee_id: str = "", manager_id: str = "", status: str = "") -> dict:
    clauses = []
    values: list[object] = []
    if employee_id:
        clauses.append("employee_id = ?")
        values.append(int(employee_id))
    if manager_id:
        clauses.append("manager_id = ?")
        values.append(int(manager_id))
    if status:
        clauses.append("status = ?")
        values.append(status)
    where = f" where {' and '.join(clauses)}" if clauses else ""
    plan_rows = conn.execute(
        f"select * from pdi_plans{where} order by due_date asc, updated_at desc, id desc",
        values,
    ).fetchall()
    plans = [public_pdi_plan(row) for row in plan_rows]
    plan_ids = [plan["id"] for plan in plans]
    if not plan_ids:
        return {"plans": [], "steps": [], "updates": [], "summary": {"active": 0, "overdue": 0, "completed": 0, "average_progress": 0}}
    placeholders = ",".join("?" for _ in plan_ids)
    steps = [public_pdi_step(row) for row in conn.execute(f"select * from pdi_steps where plan_id in ({placeholders}) order by plan_id asc, id asc", plan_ids).fetchall()]
    updates = [public_pdi_update(row) for row in conn.execute(f"select * from pdi_updates where plan_id in ({placeholders}) order by created_at desc, id desc", plan_ids).fetchall()]
    steps_by_plan = {plan_id: [] for plan_id in plan_ids}
    updates_by_plan = {plan_id: [] for plan_id in plan_ids}
    for step in steps:
        steps_by_plan.setdefault(step["plan_id"], []).append(step)
    for update in updates:
        updates_by_plan.setdefault(update["plan_id"], []).append(update)
    for plan in plans:
        plan_steps = steps_by_plan.get(plan["id"], [])
        plan_updates = updates_by_plan.get(plan["id"], [])
        plan["steps"] = plan_steps
        plan["updates"] = plan_updates
        plan["quality"] = pdi_quality(plan, plan_steps, plan_updates)
    total_progress = sum(int(plan.get("progress") or 0) for plan in plans)
    summary = {
        "active": len([plan for plan in plans if plan["status"] not in ("Concluído", "Cancelado")]),
        "overdue": len([plan for plan in plans if plan["status"] == "Atrasado"]),
        "completed": len([plan for plan in plans if plan["status"] == "Concluído"]),
        "average_progress": round(total_progress / len(plans)) if plans else 0,
    }
    return {"plans": plans, "steps": steps, "updates": updates, "summary": summary}


def generated_pdi_structure(body: dict, employee_name: str, title: str, due_date: str) -> dict:
    gap = (body.get("gaps") or "gap principal").strip()
    impact = body.get("impact_area") or "Operação interna"
    impact_map = {
        "Cliente diretamente": ["melhorar experiência do cliente", "reduzir atrito", "aumentar previsibilidade de atendimento", "diminuir reincidência"],
        "Receita": ["proteger retenção", "reduzir risco de churn", "melhorar eficiência comercial/operacional", "preservar margem quando aplicável"],
        "Operação interna": ["reduzir retrabalho", "melhorar priorização", "aumentar capacidade do time", "diminuir dependência do gestor"],
        "Clima / time": ["melhorar colaboração", "reduzir ruído", "aumentar confiança", "melhorar comunicação e alinhamento"],
    }
    return {
        "title": title,
        "objective": f"Objetivo: {(body.get('expected_change') or body.get('objective') or 'evoluir o comportamento definido pelo gestor').strip()}",
        "diagnosis": (
            f"{employee_name} está em um PDI de {body.get('pdi_type') or 'Desenvolvimento'} para trabalhar {gap}. "
            f"O plano considera o contexto atual ({body.get('current_moment') or 'momento não descrito'}), "
            f"usa como alavanca os pontos fortes observados ({body.get('strengths') or 'ainda não detalhados'}) "
            f"e acompanha impacto em {impact.lower()}."
        ),
        "signals": [
            body.get("evidences") or "Evidências registradas manualmente pelo gestor.",
            body.get("improvements") or "Comportamentos observáveis a desenvolver.",
            body.get("main_metric") or "Métrica principal ainda a calibrar.",
        ],
        "pillars": [
            {"title": "Performance individual", "text": f"Reduzir ruído em {gap}, conectando cada entrega à métrica definida."},
            {"title": "Impacto no crescimento", "text": "Melhorar cliente, operação, receita ou clima conforme o impacto selecionado."},
            {"title": "Execução acompanhada", "text": f"Criar cadência {body.get('followup_frequency') or 'regular'} para revisar progresso e remover bloqueios."},
            {"title": "Aprendizado aplicado", "text": f"Usar perfil {body.get('learning_profile') or 'não informado'} e aprendizagem por {body.get('learning_method') or 'prática'}."},
        ],
        "expected_evolution": {
            "start": "Entendimento claro do gap, compromisso assumido e comportamento esperado descrito sem ambiguidade.",
            "middle": "Execução assistida com evidências reais, menos reincidência e melhoria nos sinais acompanhados.",
            "end": "Autonomia, estabilidade do novo comportamento e reflexo em métricas de cliente, fila, qualidade, entrega ou clima.",
        },
        "company_impact": impact_map.get(impact, impact_map["Operação interna"]),
        "resources": [item.strip() for item in (body.get("resources") or "").split(",") if item.strip()],
        "checkpoints": [
            "Observar evidências de mudança, evolução da métrica principal e qualidade da comunicação de riscos.",
            "Comparar sinais operacionais, feedbacks, evolução de desempenho e evidências para validar efeito real.",
            "Ao final, comparar comportamentos antes/depois, impacto percebido e estabilidade da nova rotina.",
        ],
        "success_criteria": f'O PDI terá funcionado quando {employee_name} demonstrar evolução consistente em "{gap}", sustentar a métrica "{body.get("main_metric") or "métrica principal"}" e agir com mais autonomia dentro das responsabilidades do cargo {body.get("current_role") or "atual"}.',
        "due_date": due_date,
    }


def default_pdi_steps(body: dict) -> list[dict]:
    return [
        {
            "period": "Semana 1",
            "title": "Alinhar PDI e comportamentos observáveis",
            "description": "Revisar evidências reais com o gestor e traduzir o gap principal em 2 comportamentos observáveis na rotina.",
            "expected_evidence": "Registro do gestor + exemplo real da rotina.",
        },
        {
            "period": "Semana 1-2",
            "title": "Executar ação prática guiada",
            "description": "Usar o recurso escolhido no PDI e registrar evidências de evolução durante a execução.",
            "expected_evidence": f"Evidência de prática usando {body.get('resources') or 'recurso definido pelo gestor'}.",
        },
        {
            "period": "Semana 3-4",
            "title": "Aplicar novo comportamento em situação real",
            "description": "Rodar checkpoint conforme frequência definida e comparar contra sinais do dashboard ou evidências manuais.",
            "expected_evidence": f"Checkpoint {body.get('followup_frequency') or 'regular'} + comparação com {body.get('main_metric') or 'métrica principal'}.",
        },
        {
            "period": "Mês 2",
            "title": "Sustentar evolução com menos dependência",
            "description": "Reduzir reincidência do gap e melhorar a métrica principal sem depender do gestor em todas as decisões.",
            "expected_evidence": "Antes/depois com redução de reincidência ou melhoria objetiva.",
        },
        {
            "period": "Mês 3",
            "title": "Consolidar impacto e decidir próximo ciclo",
            "description": "Consolidar evidências, calcular impacto no time/cliente/empresa e definir encerramento ou novo objetivo.",
            "expected_evidence": "Avaliação final com impacto percebido e decisão do gestor/RH.",
        },
    ]


def sync_pdi_plan_progress(conn: sqlite3.Connection, plan_id: int, requested_status: str = "") -> sqlite3.Row:
    steps = conn.execute("select * from pdi_steps where plan_id = ?", (plan_id,)).fetchall()
    if steps:
        progress = round(sum(int(step["progress"] or 0) for step in steps) / len(steps))
    else:
        progress = 0
    plan = conn.execute("select * from pdi_plans where id = ?", (plan_id,)).fetchone()
    status = pdi_status_from_progress(progress, plan["due_date"] if plan else "", requested_status)
    now = iso(utc_now())
    conn.execute("update pdi_plans set progress = ?, status = ?, updated_at = ? where id = ?", (progress, status, now, plan_id))
    return conn.execute("select * from pdi_plans where id = ?", (plan_id,)).fetchone()


def public_career_row(row: sqlite3.Row) -> dict:
    data = row_dict(row)
    for key in ("bonus_eligible", "commission_eligible", "required", "requires_pdi_completed", "requires_manager_approval", "requires_hr_approval", "requires_director_approval", "visible_to_employee"):
        if key in data:
            data[key] = bool(data[key])
    return data


def career_payload(conn: sqlite3.Connection) -> dict:
    tables = {
        "families": "select * from career_families order by name asc",
        "tracks": "select * from career_tracks order by display_order asc, name asc",
        "levels": "select * from career_levels order by hierarchy_order asc, name asc",
        "roles": "select * from career_roles order by name asc",
        "competencies": "select * from career_competencies order by name asc",
        "role_competencies": "select * from career_role_competencies order by id asc",
        "transitions": "select * from career_transitions order by id asc",
        "assignments": """
            select a.*, u.full_name as employee_name, u.email as employee_email,
                   f.name as family_name, t.name as track_name, r.name as role_name,
                   l.name as level_name, nr.name as suggested_next_role_name
            from employee_career_assignments a
            join users u on u.id = a.employee_id
            left join career_families f on f.id = a.family_id
            left join career_tracks t on t.id = a.track_id
            left join career_roles r on r.id = a.role_id
            left join career_levels l on l.id = a.level_id
            left join career_roles nr on nr.id = a.suggested_next_role_id
            order by u.full_name asc
        """,
        "reviews": "select * from employee_career_reviews order by created_at desc",
        "actions": "select * from career_development_actions order by due_date asc, id desc",
        "movements": """
            select m.*, u.full_name as employee_name, fr.name as from_role_name, tr.name as to_role_name
            from career_movements m
            join users u on u.id = m.employee_id
            left join career_roles fr on fr.id = m.from_role_id
            left join career_roles tr on tr.id = m.to_role_id
            order by m.created_at desc
        """,
        "history": "select * from career_history order by event_date desc, id desc",
    }
    payload: dict[str, list] = {}
    for key, sql in tables.items():
        rows = conn.execute(sql).fetchall()
        payload[key] = [public_career_row(row) for row in rows]
    return payload


def readiness_for_assignment(assignment: dict, actions: list[dict], transitions: list[dict]) -> dict:
    if not assignment.get("role_id") or not assignment.get("suggested_next_role_id"):
        return {
            "score": 0,
            "label": "Sem plano definido",
            "reasons": ["Cargo atual ou próximo cargo ainda não foi configurado pelo RH."],
        }
    score = 45
    reasons = ["Cargo atual e próximo cargo definidos."]
    if assignment.get("started_at"):
        score += 15
        reasons.append("Data de entrada no cargo atual cadastrada.")
    if assignment.get("career_status") in ("Pronto para próximo nível", "Elegível para promoção"):
        score += 25
        reasons.append("Status de carreira indica proximidade de evolução.")
    employee_actions = [action for action in actions if str(action.get("employee_id")) == str(assignment.get("employee_id"))]
    open_actions = [action for action in employee_actions if action.get("status") != "Concluída"]
    if employee_actions and not open_actions:
        score += 15
        reasons.append("Ações de desenvolvimento vinculadas estão concluídas.")
    elif employee_actions:
        score += 8
        reasons.append("Há PDI ou ações de desenvolvimento em andamento.")
    else:
        reasons.append("Ainda não há ações de desenvolvimento vinculadas.")
    score = max(0, min(100, score))
    label = "Distante"
    if score >= 90:
        label = "Elegível"
    elif score >= 70:
        label = "Próximo"
    elif score >= 40:
        label = "Em desenvolvimento"
    return {"score": score, "label": label, "reasons": reasons}


def row_dict(row: sqlite3.Row | None) -> dict:
    return dict(row) if row else {}


def json_list(value: str | None) -> list:
    try:
        parsed = json.loads(value or "[]")
        return parsed if isinstance(parsed, list) else []
    except json.JSONDecodeError:
        return []


def slugify(value: str) -> str:
    text = value.lower()
    replacements = {
        "á": "a", "à": "a", "ã": "a", "â": "a", "ä": "a",
        "é": "e", "è": "e", "ê": "e", "ë": "e",
        "í": "i", "ì": "i", "î": "i", "ï": "i",
        "ó": "o", "ò": "o", "õ": "o", "ô": "o", "ö": "o",
        "ú": "u", "ù": "u", "û": "u", "ü": "u",
        "ç": "c",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or secrets.token_hex(4)


def unique_slug(conn: sqlite3.Connection, title: str) -> str:
    base = slugify(title)
    slug = base
    index = 2
    while conn.execute("select id from jobs where slug = ?", (slug,)).fetchone():
        slug = f"{base}-{index}"
        index += 1
    return slug


def default_job_stages() -> list[dict]:
    return [
        {"name": "Em aberto", "color": "#632947", "type": "Inicial"},
        {"name": "Aprovados pelo ATS", "color": "#4f8f71", "type": "Intermediária"},
        {"name": "Reprovados pelo ATS", "color": "#b84a62", "type": "Final negativa"},
        {"name": "Pré-selecionados", "color": "#4b6f9f", "type": "Intermediária"},
        {"name": "Softskill", "color": "#a66a3f", "type": "Intermediária"},
        {"name": "Hardskill", "color": "#6e5d94", "type": "Intermediária"},
        {"name": "Entrevista com gestor", "color": "#2f6f73", "type": "Intermediária"},
        {"name": "Contratados", "color": "#2f7a55", "type": "Final positiva"},
    ]


def public_job(row: sqlite3.Row, counts: dict | None = None) -> dict:
    data = row_dict(row)
    data["show_salary"] = bool(data.get("show_salary"))
    data["benefits"] = json_list(data.pop("benefits_json", "[]"))
    data["counts"] = counts or {}
    return data


def public_question(row: sqlite3.Row) -> dict:
    data = row_dict(row)
    data["options"] = json_list(data.pop("options_json", "[]"))
    data["required"] = bool(data.get("required"))
    data["knockout"] = bool(data.get("knockout"))
    return data


def public_stage(row: sqlite3.Row) -> dict:
    data = row_dict(row)
    data["active"] = bool(data.get("active"))
    return data


def public_application(row: sqlite3.Row) -> dict:
    data = row_dict(row)
    data["favorite"] = bool(data.get("favorite"))
    return data


def job_counts(conn: sqlite3.Connection, job_id: int) -> dict:
    rows = conn.execute(
        """
        select a.*, s.name as stage_name
        from applications a
        left join job_stages s on s.id = a.current_stage_id
        where a.job_id = ?
        """,
        (job_id,),
    ).fetchall()
    total = len(rows)
    approved_ats = len([row for row in rows if row["stage_name"] == "Aprovados pelo ATS" or (row["ats_score"] or 0) >= 80])
    rejected_ats = len([row for row in rows if row["stage_name"] == "Reprovados pelo ATS"])
    triage = len([row for row in rows if row["stage_name"] in ("Em aberto", "Aprovados pelo ATS", "Pré-selecionados")])
    interview = len([row for row in rows if row["stage_name"] and "Entrevista" in row["stage_name"]])
    hired = len([row for row in rows if row["stage_name"] == "Contratados"])
    average = round(sum(row["ats_score"] or 0 for row in rows) / total) if total else 0
    return {
        "total": total,
        "approved_ats": approved_ats,
        "rejected_ats": rejected_ats,
        "triage": triage,
        "interview": interview,
        "hired": hired,
        "average_score": average,
    }


def job_detail(conn: sqlite3.Connection, job_id: int) -> dict | None:
    job = conn.execute("select * from jobs where id = ?", (job_id,)).fetchone()
    if not job:
        return None
    questions = conn.execute("select * from job_questions where job_id = ? order by sort_order asc, id asc", (job_id,)).fetchall()
    stages = conn.execute("select * from job_stages where job_id = ? order by sort_order asc, id asc", (job_id,)).fetchall()
    applications = conn.execute(
        """
        select
          a.*, c.full_name, c.email, c.whatsapp, c.city, c.state, c.neighborhood,
          c.linkedin_url, c.portfolio_url, c.resume_url, c.education_level,
          c.course, c.experience_level, c.experience_summary,
          c.currently_working, c.talent_pool_accepted, s.name as stage_name
        from applications a
        join candidates c on c.id = a.candidate_id
        left join job_stages s on s.id = a.current_stage_id
        where a.job_id = ?
        order by a.created_at desc
        """,
        (job_id,),
    ).fetchall()
    return {
        "job": public_job(job, job_counts(conn, job_id)),
        "questions": [public_question(row) for row in questions],
        "stages": [public_stage(row) for row in stages],
        "applications": [public_application(row) for row in applications],
    }


def ats_analysis(job: sqlite3.Row, candidate: dict, application: dict, questions: list[sqlite3.Row], answers: dict[str, str]) -> dict:
    score = 35
    strengths: list[str] = []
    risks: list[str] = []
    incompatible_knockout = False

    if candidate.get("resume_url"):
        score += 10
        strengths.append("Currículo anexado para validação humana.")
    else:
        risks.append("Candidato ainda não anexou currículo.")

    if (application.get("accepts_work_model") or "").lower().startswith("sim"):
        score += 12
        strengths.append("Aceita a modalidade indicada para a vaga.")
    else:
        score -= 10
        risks.append("Modalidade pode exigir revisão manual.")

    salary_expectation = application.get("salary_expectation")
    salary_max = job["salary_max"]
    salary_min = job["salary_min"]
    if salary_expectation and salary_max:
        salary = float(salary_expectation)
        if salary_min and float(salary_min) <= salary <= float(salary_max):
            score += 12
            strengths.append("Pretensão salarial dentro da faixa configurada.")
        elif salary <= float(salary_max) * 1.1:
            score += 5
            risks.append("Pretensão salarial próxima da faixa.")
        else:
            score -= 12
            risks.append("Pretensão salarial acima da faixa configurada.")

    if candidate.get("education_level"):
        score += 7
    if candidate.get("experience_summary") or candidate.get("experience_level"):
        score += 10
        strengths.append("Informou experiência resumida para análise.")
    else:
        risks.append("Experiência pouco detalhada.")
    if application.get("availability_start") or application.get("availability_schedule"):
        score += 5

    for question in questions:
        answer = (answers.get(str(question["id"])) or "").strip()
        expected = (question["expected_answer"] or "").strip().lower()
        weight = max(1, min(5, int(question["weight"] or 1)))
        if answer:
            score += weight
        if question["knockout"] and expected:
            normalized = answer.lower()
            passed = expected in normalized or normalized in expected
            if passed:
                score += weight * 2
            else:
                score -= weight * 6
                incompatible_knockout = True
                risks.append(f"Resposta eliminatória incompatível: {question['question']}")

    score = max(0, min(100, int(score)))
    if score >= 80:
        classification = "Alta aderência"
        recommendation = "Aprovar pelo ATS"
    elif score >= 60:
        classification = "Média aderência"
        recommendation = "Pré-selecionar"
    elif score >= 40:
        classification = "Baixa aderência"
        recommendation = "Revisar manualmente"
    else:
        classification = "Incompatível"
        recommendation = "Reprovar pelo ATS"
    if incompatible_knockout:
        recommendation = "Revisar manualmente"
        classification = "Baixa aderência" if score >= 40 else "Incompatível"

    if not strengths:
        strengths.append("Cadastro recebido com dados básicos suficientes para triagem inicial.")
    if not risks:
        risks.append("Sem incompatibilidades objetivas identificadas nesta análise inicial.")

    return {
        "score": score,
        "classification": classification,
        "summary": "Análise inicial baseada em requisitos da vaga, disponibilidade, faixa salarial, completude do cadastro e respostas de triagem. A decisão final permanece humana.",
        "strengths": "; ".join(strengths),
        "risks": "; ".join(risks),
        "recommendation": recommendation,
    }


def find_user_by_id(conn: sqlite3.Connection, user_id: int) -> sqlite3.Row | None:
    return conn.execute("select * from users where id = ?", (user_id,)).fetchone()


def find_invite(conn: sqlite3.Connection, token: str) -> sqlite3.Row | None:
    return conn.execute("select * from users where invite_token = ?", (token,)).fetchone()


def read_body(handler: BaseHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length") or 0)
    if not length:
        return {}
    raw = handler.rfile.read(length).decode("utf-8")
    return json.loads(raw or "{}")


class PeopleHubHandler(BaseHTTPRequestHandler):
    server_version = "PeopleHubLocal/1.0"

    def log_message(self, fmt: str, *args) -> None:
        print("%s - %s" % (self.address_string(), fmt % args))

    def send_json(self, status: int, payload: dict | list) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_file(self, path: Path, content_type: str) -> None:
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        if path in ("/", "/index.html", "/vagas") or path.startswith("/convite/") or path.startswith("/vagas/"):
            self.send_file(ROOT / "outputs" / "nvoip-rh-platform.html", "text/html; charset=utf-8")
            return
        if path == "/api/health":
            self.send_json(200, {"ok": True, "database": str(DB_PATH)})
            return
        if path == "/api/employees":
            with connect() as conn:
                rows = conn.execute("select * from users order by id asc").fetchall()
            self.send_json(200, {"employees": [public_user(row) for row in rows]})
            return
        if path == "/api/posts":
            with connect() as conn:
                rows = conn.execute("select * from public_posts order by id desc").fetchall()
            self.send_json(200, {"posts": [public_post(row) for row in rows]})
            return
        if path == "/api/time-events":
            params = parse_qs(parsed.query)
            clauses = []
            values: list[object] = []
            user_id = (params.get("user_id") or [""])[0]
            event_date = (params.get("date") or [""])[0]
            event_type = (params.get("type") or [""])[0]
            if user_id:
                clauses.append("user_id = ?")
                values.append(int(user_id))
            if event_date:
                clauses.append("event_date = ?")
                values.append(event_date)
            if event_type:
                clauses.append("event_type = ?")
                values.append(event_type)
            where = f" where {' and '.join(clauses)}" if clauses else ""
            with connect() as conn:
                rows = conn.execute(
                    f"select * from time_events{where} order by event_date desc, started_at asc, id asc",
                    values,
                ).fetchall()
            self.send_json(200, {"events": [public_time_event(row) for row in rows]})
            return
        if path == "/api/compensation":
            params = parse_qs(parsed.query)
            clauses = []
            values: list[object] = []
            user_id = (params.get("user_id") or [""])[0]
            competence = (params.get("competence") or [""])[0]
            if user_id:
                clauses.append("user_id = ?")
                values.append(int(user_id))
            if competence:
                clauses.append("competence = ?")
                values.append(competence)
            where = f" where {' and '.join(clauses)}" if clauses else ""
            with connect() as conn:
                rows = conn.execute(
                    f"select * from compensation_entries{where} order by competence desc, user_name asc, id desc",
                    values,
                ).fetchall()
            self.send_json(200, {"entries": [public_compensation(row) for row in rows]})
            return
        if path == "/api/pdi":
            params = parse_qs(parsed.query)
            with connect() as conn:
                payload = pdi_payload(
                    conn,
                    employee_id=(params.get("employee_id") or [""])[0],
                    manager_id=(params.get("manager_id") or [""])[0],
                    status=(params.get("status") or [""])[0],
                )
            self.send_json(200, payload)
            return
        if path == "/api/gamification":
            params = parse_qs(parsed.query)
            with connect() as conn:
                payload = gamification_payload(conn, user_id=(params.get("user_id") or [""])[0])
            self.send_json(200, payload)
            return
        if path == "/api/career":
            with connect() as conn:
                payload = career_payload(conn)
                payload["readiness"] = [
                    {
                        "employee_id": assignment.get("employee_id"),
                        **readiness_for_assignment(assignment, payload["actions"], payload["transitions"]),
                    }
                    for assignment in payload["assignments"]
                ]
            self.send_json(200, payload)
            return
        if path == "/api/jobs":
            params = parse_qs(parsed.query)
            clauses = []
            values: list[object] = []
            status = (params.get("status") or [""])[0]
            department = (params.get("department") or [""])[0]
            work_model = (params.get("work_model") or [""])[0]
            contract_type = (params.get("contract_type") or [""])[0]
            responsible = (params.get("responsible") or [""])[0]
            search = (params.get("q") or [""])[0]
            if status:
                clauses.append("status = ?")
                values.append(status)
            if department:
                clauses.append("department = ?")
                values.append(department)
            if work_model:
                clauses.append("work_model = ?")
                values.append(work_model)
            if contract_type:
                clauses.append("contract_type = ?")
                values.append(contract_type)
            if responsible:
                clauses.append("responsible_name like ?")
                values.append(f"%{responsible}%")
            if search:
                clauses.append("(title like ? or department like ? or city like ?)")
                values.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
            where = f" where {' and '.join(clauses)}" if clauses else ""
            with connect() as conn:
                rows = conn.execute(f"select * from jobs{where} order by created_at desc, id desc", values).fetchall()
                jobs = [public_job(row, job_counts(conn, row["id"])) for row in rows]
            self.send_json(200, {"jobs": jobs})
            return
        if path.startswith("/api/jobs/"):
            try:
                job_id = int(path.strip("/").split("/")[2])
            except (IndexError, ValueError):
                self.send_json(404, {"error": "Vaga não encontrada."})
                return
            with connect() as conn:
                detail = job_detail(conn, job_id)
            if not detail:
                self.send_json(404, {"error": "Vaga não encontrada."})
                return
            self.send_json(200, detail)
            return
        if path == "/api/public/jobs":
            today = utc_now().date().isoformat()
            with connect() as conn:
                rows = conn.execute(
                    """
                    select * from jobs
                    where status = 'Publicada'
                      and (deadline is null or deadline = '' or deadline >= ?)
                    order by published_at desc, created_at desc
                    """,
                    (today,),
                ).fetchall()
                jobs = [public_job(row, job_counts(conn, row["id"])) for row in rows]
            self.send_json(200, {"jobs": jobs})
            return
        if path.startswith("/api/public/jobs/"):
            slug = path.strip("/").split("/")[-1]
            with connect() as conn:
                row = conn.execute("select * from jobs where slug = ? and status = 'Publicada'", (slug,)).fetchone()
                detail = job_detail(conn, row["id"]) if row else None
            if not detail:
                self.send_json(404, {"error": "Vaga não encontrada ou não publicada."})
                return
            self.send_json(200, detail)
            return
        if path.startswith("/api/invites/"):
            token = path.split("/")[-1]
            with connect() as conn:
                row = find_invite(conn, token)
            if not row:
                self.send_json(404, {"error": "Link não encontrado."})
                return
            user = public_user(row)
            if user["invite_status"] == "expirado":
                self.send_json(410, {"error": "Este link expirou. Peça um novo link ao RH."})
                return
            if user["invite_status"] == "usado":
                self.send_json(409, {"error": "Este link já foi usado."})
                return
            self.send_json(200, {"employee": user})
            return

        candidate = (ROOT / path.lstrip("/")).resolve()
        if ROOT in candidate.parents and candidate.exists() and candidate.is_file():
            suffix = candidate.suffix.lower()
            content_type = "text/plain; charset=utf-8"
            if suffix == ".html":
                content_type = "text/html; charset=utf-8"
            elif suffix == ".css":
                content_type = "text/css; charset=utf-8"
            elif suffix == ".js":
                content_type = "application/javascript; charset=utf-8"
            self.send_file(candidate, content_type)
            return
        self.send_json(404, {"error": "Não encontrado."})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            body = read_body(self)
        except json.JSONDecodeError:
            self.send_json(400, {"error": "JSON inválido."})
            return

        if path == "/api/login":
            email = (body.get("email") or "").strip().lower()
            password = body.get("password") or ""
            with connect() as conn:
                row = conn.execute("select * from users where lower(email) = ?", (email,)).fetchone()
            if not row:
                self.send_json(401, {"error": "Usuário não encontrado."})
                return
            if email != ADMIN_EMAIL:
                if not row["password_hash"] or row["password_hash"] != hash_password(password):
                    self.send_json(401, {"error": "Senha inválida ou primeiro acesso pendente."})
                    return
            self.send_json(200, {"user": public_user(row)})
            return

        if path == "/api/employees":
            full_name = (body.get("full_name") or "").strip()
            email = (body.get("email") or "").strip().lower()
            if not full_name or not email:
                self.send_json(400, {"error": "Nome completo e e-mail são obrigatórios."})
                return
            group = body.get("permission_group") or "Colaborador"
            token = secrets.token_urlsafe(12)
            now = iso(utc_now())
            expires = iso(utc_now() + timedelta(hours=12))
            permissions = body.get("permissions") or default_permissions(group)
            leadership = body.get("leadership") or {}
            try:
                with connect() as conn:
                    conn.execute(
                        """
                        insert into users (
                          full_name, preferred_name, email, role, department, work_mode, hired_at,
                          permission_group, is_active, must_complete_profile, permissions_json,
                          leadership_json, invite_token, invite_expires_at, created_at, updated_at
                        ) values (?, ?, ?, ?, ?, ?, ?, ?, 0, 1, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            full_name,
                            body.get("preferred_name") or "",
                            email,
                            body.get("role") or "",
                            body.get("department") or "",
                            body.get("work_mode") or "",
                            body.get("hired_at") or "",
                            group,
                            json.dumps(permissions, ensure_ascii=False),
                            json.dumps(leadership, ensure_ascii=False),
                            token,
                            expires,
                            now,
                            now,
                        ),
                    )
                    row = conn.execute("select * from users where lower(email) = ?", (email,)).fetchone()
            except sqlite3.IntegrityError:
                self.send_json(409, {"error": "Já existe colaborador com este e-mail."})
                return
            self.send_json(201, {"employee": public_user(row)})
            return

        if path == "/api/posts":
            text = (body.get("text") or "").strip()
            if not text:
                self.send_json(400, {"error": "Escreva uma mensagem para publicar no mural."})
                return
            author_id = body.get("author_id")
            now = iso(utc_now())
            with connect() as conn:
                author = find_user_by_id(conn, int(author_id)) if author_id else None
                if not author:
                    author = conn.execute("select * from users where lower(email) = ?", (ADMIN_EMAIL,)).fetchone()
                author_name = author["preferred_name"] or author["full_name"] if author else "Nvoip"
                conn.execute(
                    """
                    insert into public_posts (author_id, author_name, text, reactions_json, created_at, updated_at)
                    values (?, ?, ?, '{}', ?, ?)
                    """,
                    (author["id"] if author else None, author_name, text, now, now),
                )
                row = conn.execute("select * from public_posts order by id desc limit 1").fetchone()
            self.send_json(201, {"post": public_post(row)})
            return

        if path.startswith("/api/posts/") and path.endswith("/react"):
            parts = path.strip("/").split("/")
            post_id = int(parts[2])
            emoji = (body.get("emoji") or "").strip()
            if not emoji:
                self.send_json(400, {"error": "Escolha uma reação."})
                return
            now = iso(utc_now())
            with connect() as conn:
                row = conn.execute("select * from public_posts where id = ?", (post_id,)).fetchone()
                if not row:
                    self.send_json(404, {"error": "Mensagem não encontrada."})
                    return
                reactions = json.loads(row["reactions_json"] or "{}")
                reactions[emoji] = int(reactions.get(emoji, 0)) + 1
                conn.execute(
                    "update public_posts set reactions_json = ?, updated_at = ? where id = ?",
                    (json.dumps(reactions, ensure_ascii=False), now, post_id),
                )
                row = conn.execute("select * from public_posts where id = ?", (post_id,)).fetchone()
            self.send_json(200, {"post": public_post(row)})
            return

        if path == "/api/time-events":
            user_id = body.get("user_id")
            event_type = (body.get("event_type") or "").strip()
            title = (body.get("title") or "").strip()
            event_date = (body.get("event_date") or "").strip()
            duration_minutes = int(body.get("duration_minutes") or 0)
            if not event_type or not title or not event_date:
                self.send_json(400, {"error": "Tipo, título e data são obrigatórios."})
                return
            now = iso(utc_now())
            with connect() as conn:
                user = find_user_by_id(conn, int(user_id)) if user_id else None
                if not user:
                    user = conn.execute("select * from users where lower(email) = ?", (ADMIN_EMAIL,)).fetchone()
                user_name = user["preferred_name"] or user["full_name"] if user else "Colaborador"
                conn.execute(
                    """
                    insert into time_events (
                      user_id, user_name, event_date, event_type, title, started_at,
                      ended_at, duration_minutes, notes, created_at, updated_at
                    ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user["id"] if user else None,
                        user_name,
                        event_date,
                        event_type,
                        title,
                        body.get("started_at") or "",
                        body.get("ended_at") or "",
                        max(0, duration_minutes),
                        body.get("notes") or "",
                        now,
                        now,
                    ),
                )
                row = conn.execute("select * from time_events order by id desc limit 1").fetchone()
            self.send_json(201, {"event": public_time_event(row)})
            return

        if path == "/api/compensation":
            user_id = body.get("user_id")
            competence = (body.get("competence") or "").strip()
            if not user_id or not competence:
                self.send_json(400, {"error": "Colaborador e competência são obrigatórios."})
                return
            def money_value(key: str) -> float:
                try:
                    return float(body.get(key) or 0)
                except (TypeError, ValueError):
                    return 0.0
            now = iso(utc_now())
            with connect() as conn:
                user = find_user_by_id(conn, int(user_id))
                if not user:
                    self.send_json(404, {"error": "Colaborador não encontrado."})
                    return
                user_name = user["preferred_name"] or user["full_name"]
                conn.execute(
                    """
                    insert into compensation_entries (
                      user_id, user_name, competence, salary_base, commission, bonus,
                      plr, va, vr, vt, cost_allowance, reimbursements, dailies,
                      discounts, status, notes, created_at, updated_at
                    ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user["id"],
                        user_name,
                        competence,
                        money_value("salary_base"),
                        money_value("commission"),
                        money_value("bonus"),
                        money_value("plr"),
                        money_value("va"),
                        money_value("vr"),
                        money_value("vt"),
                        money_value("cost_allowance"),
                        money_value("reimbursements"),
                        money_value("dailies"),
                        money_value("discounts"),
                        body.get("status") or "Rascunho",
                        body.get("notes") or "",
                        now,
                        now,
                    ),
                )
                row = conn.execute("select * from compensation_entries order by id desc limit 1").fetchone()
            self.send_json(201, {"entry": public_compensation(row)})
            return

        if path == "/api/pdi/plans":
            employee_id = body.get("employee_id")
            if not employee_id:
                self.send_json(400, {"error": "Selecione o colaborador do PDI."})
                return
            pdi_type = (body.get("pdi_type") or "Desenvolvimento").strip()
            gap = (body.get("gaps") or "").strip()
            expected_change = (body.get("expected_change") or "").strip()
            if not gap or not expected_change:
                self.send_json(400, {"error": "Gap principal e mudança esperada são obrigatórios."})
                return
            now = iso(utc_now())
            due_date = (body.get("due_date") or "").strip()
            title = (body.get("title") or "").strip() or f"{pdi_type}: {gap}"
            with connect() as conn:
                employee = find_user_by_id(conn, int(employee_id))
                if not employee:
                    self.send_json(404, {"error": "Colaborador não encontrado."})
                    return
                manager = find_user_by_id(conn, int(body.get("manager_id"))) if body.get("manager_id") else None
                manager_name = (manager["preferred_name"] or manager["full_name"]) if manager else (body.get("manager_name") or "Gestor/RH")
                employee_name = employee["preferred_name"] or employee["full_name"]
                structured = generated_pdi_structure(body, employee_name, title, due_date)
                diagnosis = structured["diagnosis"]
                success_criteria = structured["success_criteria"]
                conn.execute(
                    """
                    insert into pdi_plans (
                      employee_id, employee_name, manager_id, manager_name, title, pdi_type,
                      status, urgency, progress, current_role, team, current_level,
                      main_responsibilities, current_moment, strengths, strengths_description,
                      gaps, improvements, evidences, recognition, feedback_reaction,
                      expected_change, impact_area, learning_profile, learning_method,
                      resources, followup_frequency, expected_term, main_metric, due_date,
                      objective, diagnosis, success_criteria, structured_json,
                      final_evaluation, created_at, updated_at
                    ) values (?, ?, ?, ?, ?, ?, 'Aberto', ?, 0, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '', ?, ?)
                    """,
                    (
                        employee["id"],
                        employee_name,
                        manager["id"] if manager else body.get("manager_id"),
                        manager_name,
                        title,
                        pdi_type,
                        body.get("urgency") or "Médio",
                        body.get("current_role") or employee["role"] or "",
                        body.get("team") or employee["department"] or "",
                        body.get("current_level") or "",
                        body.get("main_responsibilities") or "",
                        body.get("current_moment") or "",
                        body.get("strengths") or "",
                        body.get("strengths_description") or "",
                        gap,
                        body.get("improvements") or "",
                        body.get("evidences") or "",
                        body.get("recognition") or "",
                        body.get("feedback_reaction") or "",
                        expected_change,
                        body.get("impact_area") or "Operação interna",
                        body.get("learning_profile") or "",
                        body.get("learning_method") or "",
                        body.get("resources") or "",
                        body.get("followup_frequency") or "Quinzenal",
                        body.get("expected_term") or "90 dias",
                        body.get("main_metric") or "",
                        due_date,
                        structured["objective"],
                        diagnosis,
                        success_criteria,
                        json.dumps(structured, ensure_ascii=False),
                        now,
                        now,
                    ),
                )
                plan_id = conn.execute("select last_insert_rowid() as id").fetchone()["id"]
                for step in default_pdi_steps(body):
                    conn.execute(
                        """
                        insert into pdi_steps (
                          plan_id, period, title, description, expected_evidence,
                          due_date, status, progress, created_at, updated_at
                        ) values (?, ?, ?, ?, ?, ?, 'Pendente', 0, ?, ?)
                        """,
                        (
                            plan_id,
                            step["period"],
                            step["title"],
                            step["description"],
                            step["expected_evidence"],
                            due_date,
                            now,
                            now,
                        ),
                    )
                conn.execute(
                    """
                    insert into pdi_updates (plan_id, author_id, author_name, author_role, update_type, comment, progress, created_at)
                    values (?, ?, ?, ?, 'Criação', ?, 0, ?)
                    """,
                    (
                        plan_id,
                        manager["id"] if manager else body.get("manager_id"),
                        manager_name,
                        body.get("author_role") or "Gestor/RH",
                        "PDI criado com diagnóstico, evidências, milestones e critério de sucesso.",
                        now,
                    ),
                )
                payload = pdi_payload(conn)
            self.send_json(201, payload)
            return

        if path == "/api/gamification/campaigns":
            name = (body.get("name") or "").strip()
            if not name:
                self.send_json(400, {"error": "Nome da campanha é obrigatório."})
                return
            now = iso(utc_now())
            participants_body = body.get("participants") or []
            metrics_body = body.get("metrics") or []
            missions_body = body.get("missions") or []
            rewards_body = body.get("rewards") or []
            with connect() as conn:
                creator = find_user_by_id(conn, int(body.get("created_by"))) if body.get("created_by") else None
                creator_name = (creator["preferred_name"] or creator["full_name"]) if creator else body.get("created_by_name") or "Gestor/RH"
                weights = body.get("score_weights") or {"resultado": 40, "qualidade": 40, "engajamento": 20}
                conn.execute(
                    """
                    insert into gamification_campaigns (
                      name, description, objective, theme, campaign_type, status,
                      start_date, end_date, visibility, created_by, created_by_name,
                      department_scope, participation_mode, scoring_mode, leaderboard_type,
                      reward_policy, healthy_mode, score_weights_json, rules_summary,
                      settings_json, created_at, updated_at
                    ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        name,
                        body.get("description") or "",
                        body.get("objective") or "",
                        body.get("theme") or "Missão corporativa",
                        body.get("campaign_type") or "Missões individuais",
                        body.get("status") or "Rascunho",
                        body.get("start_date") or "",
                        body.get("end_date") or "",
                        body.get("visibility") or "Participantes",
                        creator["id"] if creator else body.get("created_by"),
                        creator_name,
                        body.get("department_scope") or "",
                        body.get("participation_mode") or "Individual",
                        body.get("scoring_mode") or "Manual",
                        body.get("leaderboard_type") or "Ranking competitivo",
                        body.get("reward_policy") or "",
                        1 if body.get("healthy_mode", True) else 0,
                        json.dumps(weights, ensure_ascii=False),
                        body.get("rules_summary") or "",
                        json.dumps(body.get("settings") or {}, ensure_ascii=False),
                        now,
                        now,
                    ),
                )
                campaign_id = conn.execute("select last_insert_rowid() as id").fetchone()["id"]
                for participant in participants_body:
                    user_id = participant.get("user_id") if isinstance(participant, dict) else participant
                    user = find_user_by_id(conn, int(user_id)) if user_id else None
                    if not user:
                        continue
                    conn.execute(
                        """
                        insert into gamification_participants (
                          campaign_id, user_id, user_name, team_name, status, joined_at, updated_at
                        ) values (?, ?, ?, ?, 'Ativo', ?, ?)
                        """,
                        (
                            campaign_id,
                            user["id"],
                            user["preferred_name"] or user["full_name"],
                            participant.get("team_name") if isinstance(participant, dict) else user["department"],
                            now,
                            now,
                        ),
                    )
                for metric in metrics_body:
                    metric_name = (metric.get("name") or "").strip()
                    if not metric_name:
                        continue
                    conn.execute(
                        """
                        insert into gamification_metrics (
                          campaign_id, name, description, score_type, source_type, source_config,
                          points, negative_points, weight, max_points_per_day, max_points_per_week,
                          approval_required, tiebreaker, multiplier, recurrence, active, created_at, updated_at
                        ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
                        """,
                        (
                            campaign_id,
                            metric_name,
                            metric.get("description") or "",
                            metric.get("score_type") or "Resultado",
                            metric.get("source_type") or body.get("scoring_mode") or "Manual",
                            json.dumps(metric.get("source_config") or {}, ensure_ascii=False),
                            int(metric.get("points") or 0),
                            int(metric.get("negative_points") or 0),
                            float(metric.get("weight") or 1),
                            int(metric["max_points_per_day"]) if metric.get("max_points_per_day") else None,
                            int(metric["max_points_per_week"]) if metric.get("max_points_per_week") else None,
                            1 if metric.get("approval_required") else 0,
                            metric.get("tiebreaker") or "",
                            float(metric.get("multiplier") or 1),
                            metric.get("recurrence") or "",
                            now,
                            now,
                        ),
                    )
                for mission in missions_body:
                    title = (mission.get("title") or "").strip()
                    if not title:
                        continue
                    conn.execute(
                        """
                        insert into gamification_missions (
                          campaign_id, title, description, points, deadline, mission_type,
                          completion_type, approval_required, evidence_required, required,
                          unlock_badge, unlock_reward_id, phase_name, active, created_at, updated_at
                        ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
                        """,
                        (
                            campaign_id,
                            title,
                            mission.get("description") or "",
                            int(mission.get("points") or 0),
                            mission.get("deadline") or "",
                            mission.get("mission_type") or "Individual",
                            mission.get("completion_type") or "Evidência",
                            1 if mission.get("approval_required") else 0,
                            1 if mission.get("evidence_required") else 0,
                            1 if mission.get("required") else 0,
                            mission.get("unlock_badge") or "",
                            mission.get("unlock_reward_id"),
                            mission.get("phase_name") or "",
                            now,
                            now,
                        ),
                    )
                for reward in rewards_body:
                    reward_name = (reward.get("name") or "").strip()
                    if not reward_name:
                        continue
                    conn.execute(
                        """
                        insert into gamification_rewards (
                          campaign_id, name, description, reward_type, cost_in_coins, stock,
                          image_url, approval_required, valid_until, eligibility_rules,
                          active, created_at, updated_at
                        ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
                        """,
                        (
                            campaign_id,
                            reward_name,
                            reward.get("description") or "",
                            reward.get("reward_type") or "Simbólica",
                            int(reward.get("cost_in_coins") or 0),
                            int(reward["stock"]) if reward.get("stock") else None,
                            reward.get("image_url") or "",
                            1 if reward.get("approval_required") else 0,
                            reward.get("valid_until") or "",
                            reward.get("eligibility_rules") or "",
                            now,
                            now,
                        ),
                    )
                payload = gamification_payload(conn)
            self.send_json(201, payload)
            return

        if path == "/api/gamification/events":
            campaign_id = body.get("campaign_id")
            participant_id = body.get("participant_id")
            points = int(body.get("points") or 0)
            justification = (body.get("justification") or "").strip()
            if not campaign_id or not participant_id:
                self.send_json(400, {"error": "Campanha e participante são obrigatórios."})
                return
            if not justification:
                self.send_json(400, {"error": "Justificativa é obrigatória para pontuação manual."})
                return
            now = iso(utc_now())
            with connect() as conn:
                participant = conn.execute("select * from gamification_participants where id = ? and campaign_id = ?", (participant_id, campaign_id)).fetchone()
                if not participant:
                    self.send_json(404, {"error": "Participante não encontrado nesta campanha."})
                    return
                creator = find_user_by_id(conn, int(body.get("created_by"))) if body.get("created_by") else None
                creator_name = (creator["preferred_name"] or creator["full_name"]) if creator else body.get("created_by_name") or "Gestor/RH"
                conn.execute(
                    """
                    insert into gamification_events (
                      campaign_id, participant_id, metric_id, mission_id, event_type,
                      points, coins, source, evidence_url, justification, status,
                      approved_by, approved_by_name, created_by, created_by_name, created_at
                    ) values (?, ?, ?, ?, ?, ?, ?, 'Manual', ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        campaign_id,
                        participant_id,
                        body.get("metric_id"),
                        body.get("mission_id"),
                        body.get("event_type") or "Pontuação manual",
                        points,
                        int(body.get("coins") or max(0, points)),
                        body.get("evidence_url") or "",
                        justification,
                        body.get("status") or "Aprovado",
                        creator["id"] if creator else body.get("created_by"),
                        creator_name,
                        creator["id"] if creator else body.get("created_by"),
                        creator_name,
                        now,
                    ),
                )
                refresh_gamification_ranking(conn, int(campaign_id))
                payload = gamification_payload(conn)
            self.send_json(201, payload)
            return

        if path.startswith("/api/pdi/steps/"):
            try:
                step_id = int(path.strip("/").split("/")[3])
            except (IndexError, ValueError):
                self.send_json(404, {"error": "Etapa do PDI não encontrada."})
                return
            now = iso(utc_now())
            status = body.get("status") or "Em andamento"
            progress = max(0, min(100, int(body.get("progress") or (100 if status == "Concluído" else 50))))
            if progress >= 100:
                status = "Concluído"
            elif progress > 0 and status == "Pendente":
                status = "Em andamento"
            with connect() as conn:
                step = conn.execute("select * from pdi_steps where id = ?", (step_id,)).fetchone()
                if not step:
                    self.send_json(404, {"error": "Etapa do PDI não encontrada."})
                    return
                conn.execute(
                    """
                    update pdi_steps
                    set status = ?, progress = ?, evidence = ?, employee_comment = ?,
                        manager_comment = ?, completed_at = ?, updated_at = ?
                    where id = ?
                    """,
                    (
                        status,
                        progress,
                        body.get("evidence") or step["evidence"] or "",
                        body.get("employee_comment") or step["employee_comment"] or "",
                        body.get("manager_comment") or step["manager_comment"] or "",
                        now if status == "Concluído" else step["completed_at"],
                        now,
                        step_id,
                    ),
                )
                sync_pdi_plan_progress(conn, int(step["plan_id"]))
                author_id = body.get("author_id")
                author = find_user_by_id(conn, int(author_id)) if author_id else None
                author_name = (author["preferred_name"] or author["full_name"]) if author else (body.get("author_name") or "Colaborador")
                conn.execute(
                    """
                    insert into pdi_updates (
                      plan_id, step_id, author_id, author_name, author_role,
                      update_type, comment, evidence, progress, created_at
                    ) values (?, ?, ?, ?, ?, 'Evolução', ?, ?, ?, ?)
                    """,
                    (
                        step["plan_id"],
                        step_id,
                        author["id"] if author else author_id,
                        author_name,
                        body.get("author_role") or "",
                        body.get("comment") or body.get("employee_comment") or body.get("manager_comment") or "Etapa atualizada.",
                        body.get("evidence") or "",
                        progress,
                        now,
                    ),
                )
                payload = pdi_payload(conn)
            self.send_json(200, payload)
            return

        if path.startswith("/api/pdi/plans/") and path.endswith("/updates"):
            parts = path.strip("/").split("/")
            try:
                plan_id = int(parts[3])
            except (IndexError, ValueError):
                self.send_json(404, {"error": "PDI não encontrado."})
                return
            now = iso(utc_now())
            with connect() as conn:
                plan = conn.execute("select * from pdi_plans where id = ?", (plan_id,)).fetchone()
                if not plan:
                    self.send_json(404, {"error": "PDI não encontrado."})
                    return
                author_id = body.get("author_id")
                author = find_user_by_id(conn, int(author_id)) if author_id else None
                author_name = (author["preferred_name"] or author["full_name"]) if author else (body.get("author_name") or "Gestor/RH")
                requested_status = body.get("status") or ""
                final_evaluation = body.get("final_evaluation") or plan["final_evaluation"] or ""
                if requested_status:
                    progress = 100 if requested_status == "Concluído" else int(plan["progress"] or 0)
                    status = pdi_status_from_progress(progress, plan["due_date"], requested_status)
                    conn.execute(
                        "update pdi_plans set status = ?, progress = ?, final_evaluation = ?, updated_at = ? where id = ?",
                        (status, progress, final_evaluation, now, plan_id),
                    )
                conn.execute(
                    """
                    insert into pdi_updates (
                      plan_id, author_id, author_name, author_role, update_type,
                      comment, evidence, progress, created_at
                    ) values (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        plan_id,
                        author["id"] if author else author_id,
                        author_name,
                        body.get("author_role") or "Gestor/RH",
                        body.get("update_type") or "Checkpoint",
                        body.get("comment") or "",
                        body.get("evidence") or "",
                        body.get("progress") if body.get("progress") is not None else plan["progress"],
                        now,
                    ),
                )
                payload = pdi_payload(conn)
            self.send_json(200, payload)
            return

        if path.startswith("/api/career/"):
            entity = path.strip("/").split("/")[2]
            now = iso(utc_now())
            with connect() as conn:
                if entity == "families":
                    name = (body.get("name") or "").strip()
                    if not name:
                        self.send_json(400, {"error": "Nome da família é obrigatório."})
                        return
                    conn.execute(
                        "insert into career_families (name, description, owner_id, status, created_at, updated_at) values (?, ?, ?, ?, ?, ?)",
                        (name, body.get("description") or "", body.get("owner_id"), body.get("status") or "Ativa", now, now),
                    )
                elif entity == "tracks":
                    name = (body.get("name") or "").strip()
                    if not name:
                        self.send_json(400, {"error": "Nome da trilha é obrigatório."})
                        return
                    conn.execute(
                        """
                        insert into career_tracks (family_id, name, description, type, display_order, status, created_at, updated_at)
                        values (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (body.get("family_id"), name, body.get("description") or "", body.get("type") or "Técnica", int(body.get("display_order") or 0), body.get("status") or "Ativa", now, now),
                    )
                elif entity == "levels":
                    name = (body.get("name") or "").strip()
                    if not name:
                        self.send_json(400, {"error": "Nome do nível é obrigatório."})
                        return
                    conn.execute(
                        """
                        insert into career_levels (name, description, hierarchy_order, seniority_weight, status, created_at, updated_at)
                        values (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (name, body.get("description") or "", int(body.get("hierarchy_order") or 0), int(body.get("seniority_weight") or 0), body.get("status") or "Ativo", now, now),
                    )
                elif entity == "roles":
                    name = (body.get("name") or "").strip()
                    if not name:
                        self.send_json(400, {"error": "Nome do cargo é obrigatório."})
                        return
                    conn.execute(
                        """
                        insert into career_roles (
                          family_id, track_id, level_id, name, mission, description,
                          responsibilities, expected_deliverables, required_requirements,
                          desired_requirements, recommended_courses, min_time_months,
                          salary_min, salary_mid, salary_max, salary_visibility,
                          bonus_eligible, commission_eligible, status, created_at, updated_at
                        ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            body.get("family_id"), body.get("track_id"), body.get("level_id"), name,
                            body.get("mission") or "", body.get("description") or "",
                            body.get("responsibilities") or "", body.get("expected_deliverables") or "",
                            body.get("required_requirements") or "", body.get("desired_requirements") or "",
                            body.get("recommended_courses") or "", int(body.get("min_time_months") or 0),
                            float(body["salary_min"]) if body.get("salary_min") else None,
                            float(body["salary_mid"]) if body.get("salary_mid") else None,
                            float(body["salary_max"]) if body.get("salary_max") else None,
                            body.get("salary_visibility") or "Restrita",
                            1 if body.get("bonus_eligible") else 0,
                            1 if body.get("commission_eligible") else 0,
                            body.get("status") or "Ativo", now, now,
                        ),
                    )
                elif entity == "competencies":
                    name = (body.get("name") or "").strip()
                    if not name:
                        self.send_json(400, {"error": "Nome da competência é obrigatório."})
                        return
                    conn.execute(
                        """
                        insert into career_competencies (name, type, description, behavior_examples, status, created_at, updated_at)
                        values (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (name, body.get("type") or "Comportamental", body.get("description") or "", body.get("behavior_examples") or "", body.get("status") or "Ativa", now, now),
                    )
                elif entity == "role-competencies":
                    conn.execute(
                        """
                        insert into career_role_competencies (
                          role_id, competency_id, expected_level, weight, required, role_specific_description, created_at, updated_at
                        ) values (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (body.get("role_id"), body.get("competency_id"), body.get("expected_level") or "Intermediário", int(body.get("weight") or 1), 1 if body.get("required", True) else 0, body.get("role_specific_description") or "", now, now),
                    )
                elif entity == "transitions":
                    conn.execute(
                        """
                        insert into career_transitions (
                          from_role_id, to_role_id, transition_type, min_time_months,
                          required_performance_score, required_360_score, requires_pdi_completed,
                          requires_manager_approval, requires_hr_approval, requires_director_approval,
                          criteria_description, status, created_at, updated_at
                        ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            body.get("from_role_id"), body.get("to_role_id"), body.get("transition_type") or "Promoção",
                            int(body.get("min_time_months") or 0),
                            float(body["required_performance_score"]) if body.get("required_performance_score") else None,
                            float(body["required_360_score"]) if body.get("required_360_score") else None,
                            1 if body.get("requires_pdi_completed") else 0,
                            1 if body.get("requires_manager_approval", True) else 0,
                            1 if body.get("requires_hr_approval", True) else 0,
                            1 if body.get("requires_director_approval") else 0,
                            body.get("criteria_description") or "", body.get("status") or "Ativa", now, now,
                        ),
                    )
                elif entity == "assignments":
                    employee_id = body.get("employee_id")
                    if not employee_id:
                        self.send_json(400, {"error": "Colaborador é obrigatório."})
                        return
                    conn.execute(
                        """
                        insert into employee_career_assignments (
                          employee_id, family_id, track_id, role_id, level_id, manager_id,
                          started_at, last_movement_at, suggested_next_role_id,
                          career_status, hr_notes, manager_notes, visible_to_employee,
                          created_at, updated_at
                        ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            employee_id, body.get("family_id"), body.get("track_id"), body.get("role_id"),
                            body.get("level_id"), body.get("manager_id"), body.get("started_at") or "",
                            body.get("last_movement_at") or "", body.get("suggested_next_role_id"),
                            body.get("career_status") or "Em desenvolvimento", body.get("hr_notes") or "",
                            body.get("manager_notes") or "", 1 if body.get("visible_to_employee", True) else 0,
                            now, now,
                        ),
                    )
                elif entity == "actions":
                    title = (body.get("title") or "").strip()
                    employee_id = body.get("employee_id")
                    if not employee_id or not title:
                        self.send_json(400, {"error": "Colaborador e ação são obrigatórios."})
                        return
                    conn.execute(
                        """
                        insert into career_development_actions (
                          employee_id, competency_id, role_id, target_role_id, pdi_action_id,
                          title, description, due_date, status, created_at, updated_at
                        ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (employee_id, body.get("competency_id"), body.get("role_id"), body.get("target_role_id"), body.get("pdi_action_id"), title, body.get("description") or "", body.get("due_date") or "", body.get("status") or "Aberta", now, now),
                    )
                elif entity == "movements":
                    employee_id = body.get("employee_id")
                    if not employee_id:
                        self.send_json(400, {"error": "Colaborador é obrigatório."})
                        return
                    conn.execute(
                        """
                        insert into career_movements (
                          employee_id, from_role_id, to_role_id, requested_by, movement_type,
                          reason, status, effective_date, created_at, updated_at
                        ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (employee_id, body.get("from_role_id"), body.get("to_role_id"), body.get("requested_by"), body.get("movement_type") or "Promoção", body.get("reason") or "", body.get("status") or "Em análise pelo RH", body.get("effective_date") or "", now, now),
                    )
                else:
                    self.send_json(404, {"error": "Entidade de carreira não encontrada."})
                    return
                payload = career_payload(conn)
                payload["readiness"] = [
                    {"employee_id": assignment.get("employee_id"), **readiness_for_assignment(assignment, payload["actions"], payload["transitions"])}
                    for assignment in payload["assignments"]
                ]
            self.send_json(201, payload)
            return

        if path == "/api/jobs":
            title = (body.get("title") or "").strip()
            if not title:
                self.send_json(400, {"error": "Título da vaga é obrigatório."})
                return
            now_dt = utc_now()
            now = iso(now_dt)
            status = body.get("status") or "Rascunho"
            published_at = iso(now_dt) if status == "Publicada" else ""
            benefits = body.get("benefits") or []
            questions = body.get("questions") or []
            stages = body.get("stages") or default_job_stages()
            with connect() as conn:
                slug = unique_slug(conn, title)
                responsible_id = body.get("responsible_user_id")
                responsible_name = (body.get("responsible_name") or "").strip()
                if responsible_id and not responsible_name:
                    responsible = find_user_by_id(conn, int(responsible_id))
                    responsible_name = responsible["preferred_name"] or responsible["full_name"] if responsible else ""
                conn.execute(
                    """
                    insert into jobs (
                      title, department, level, quantity, contract_type, work_model, city,
                      work_location, journey, working_hours, salary_min, salary_max,
                      salary_text, show_salary, benefits_json, additional_benefits,
                      summary, responsibilities, required_requirements, desired_requirements,
                      education_level, experience_level, behavioral_profile, internal_notes,
                      responsible_user_id, responsible_name, deadline, status, slug,
                      published_at, created_at, updated_at
                    ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        title,
                        body.get("department") or "",
                        body.get("level") or "",
                        int(body.get("quantity") or 1),
                        body.get("contract_type") or "",
                        body.get("work_model") or "",
                        body.get("city") or "",
                        body.get("work_location") or "",
                        body.get("journey") or "",
                        body.get("working_hours") or "",
                        float(body["salary_min"]) if body.get("salary_min") else None,
                        float(body["salary_max"]) if body.get("salary_max") else None,
                        body.get("salary_text") or "",
                        1 if body.get("show_salary") else 0,
                        json.dumps(benefits, ensure_ascii=False),
                        body.get("additional_benefits") or "",
                        body.get("summary") or "",
                        body.get("responsibilities") or "",
                        body.get("required_requirements") or "",
                        body.get("desired_requirements") or "",
                        body.get("education_level") or "",
                        body.get("experience_level") or "",
                        body.get("behavioral_profile") or "",
                        body.get("internal_notes") or "",
                        int(responsible_id) if responsible_id else None,
                        responsible_name,
                        body.get("deadline") or "",
                        status,
                        slug,
                        published_at,
                        now,
                        now,
                    ),
                )
                job_id = conn.execute("select last_insert_rowid() as id").fetchone()["id"]
                for index, stage in enumerate(stages):
                    name = (stage.get("name") if isinstance(stage, dict) else str(stage)).strip()
                    if not name:
                        continue
                    conn.execute(
                        """
                        insert into job_stages (job_id, name, sort_order, color, type, active, created_at)
                        values (?, ?, ?, ?, ?, 1, ?)
                        """,
                        (
                            job_id,
                            name,
                            index,
                            stage.get("color") if isinstance(stage, dict) else "#632947",
                            stage.get("type") if isinstance(stage, dict) else "Intermediária",
                            now,
                        ),
                    )
                for index, question in enumerate(questions):
                    text = (question.get("question") or "").strip()
                    if not text:
                        continue
                    conn.execute(
                        """
                        insert into job_questions (
                          job_id, question, answer_type, options_json, required,
                          knockout, expected_answer, weight, sort_order, created_at
                        ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            job_id,
                            text,
                            question.get("answer_type") or "Texto curto",
                            json.dumps(question.get("options") or [], ensure_ascii=False),
                            1 if question.get("required") else 0,
                            1 if question.get("knockout") else 0,
                            question.get("expected_answer") or "",
                            max(1, min(5, int(question.get("weight") or 1))),
                            index,
                            now,
                        ),
                    )
                detail = job_detail(conn, job_id)
            self.send_json(201, detail or {})
            return

        if path.startswith("/api/public/jobs/") and path.endswith("/apply"):
            parts = path.strip("/").split("/")
            try:
                job_id = int(parts[3])
            except (IndexError, ValueError):
                self.send_json(404, {"error": "Vaga não encontrada."})
                return
            candidate_body = body.get("candidate") or {}
            application_body = body.get("application") or {}
            answers_body = body.get("answers") or {}
            full_name = (candidate_body.get("full_name") or "").strip()
            email = (candidate_body.get("email") or "").strip().lower()
            if not full_name or not email:
                self.send_json(400, {"error": "Nome completo e e-mail são obrigatórios."})
                return
            if not candidate_body.get("lgpd_accepted"):
                self.send_json(400, {"error": "O aceite LGPD é obrigatório para candidatura."})
                return
            now = iso(utc_now())
            with connect() as conn:
                job = conn.execute("select * from jobs where id = ? and status = 'Publicada'", (job_id,)).fetchone()
                if not job:
                    self.send_json(404, {"error": "Vaga não encontrada ou não publicada."})
                    return
                conn.execute(
                    """
                    insert into candidates (
                      full_name, email, whatsapp, city, state, neighborhood, linkedin_url,
                      portfolio_url, resume_url, education_level, course, experience_level,
                      experience_summary, currently_working, talent_pool_accepted,
                      lgpd_accepted, created_at, updated_at
                    ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        full_name,
                        email,
                        candidate_body.get("whatsapp") or "",
                        candidate_body.get("city") or "",
                        candidate_body.get("state") or "",
                        candidate_body.get("neighborhood") or "",
                        candidate_body.get("linkedin_url") or "",
                        candidate_body.get("portfolio_url") or "",
                        candidate_body.get("resume_url") or "",
                        candidate_body.get("education_level") or "",
                        candidate_body.get("course") or "",
                        candidate_body.get("experience_level") or "",
                        candidate_body.get("experience_summary") or "",
                        candidate_body.get("currently_working") or "",
                        1 if candidate_body.get("talent_pool_accepted") else 0,
                        1,
                        now,
                        now,
                    ),
                )
                candidate_id = conn.execute("select last_insert_rowid() as id").fetchone()["id"]
                questions = conn.execute("select * from job_questions where job_id = ? order by sort_order asc, id asc", (job_id,)).fetchall()
                analysis = ats_analysis(job, candidate_body, application_body, questions, answers_body)
                target_stage_name = "Em aberto"
                if analysis["recommendation"] == "Aprovar pelo ATS":
                    target_stage_name = "Aprovados pelo ATS"
                elif analysis["recommendation"] == "Reprovar pelo ATS":
                    target_stage_name = "Reprovados pelo ATS"
                stage = conn.execute(
                    "select * from job_stages where job_id = ? and name = ? order by sort_order asc limit 1",
                    (job_id, target_stage_name),
                ).fetchone()
                if not stage:
                    stage = conn.execute("select * from job_stages where job_id = ? order by sort_order asc limit 1", (job_id,)).fetchone()
                conn.execute(
                    """
                    insert into applications (
                      job_id, candidate_id, current_stage_id, salary_expectation,
                      availability_start, availability_schedule, accepts_work_model,
                      ats_score, ats_classification, ats_summary, ats_strengths,
                      ats_risks, ats_recommendation, status, created_at, updated_at
                    ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        job_id,
                        candidate_id,
                        stage["id"] if stage else None,
                        float(application_body["salary_expectation"]) if application_body.get("salary_expectation") else None,
                        application_body.get("availability_start") or "",
                        application_body.get("availability_schedule") or "",
                        application_body.get("accepts_work_model") or "",
                        analysis["score"],
                        analysis["classification"],
                        analysis["summary"],
                        analysis["strengths"],
                        analysis["risks"],
                        analysis["recommendation"],
                        "Em aberto",
                        now,
                        now,
                    ),
                )
                application_id = conn.execute("select last_insert_rowid() as id").fetchone()["id"]
                for question in questions:
                    answer = (answers_body.get(str(question["id"])) or "").strip()
                    expected = (question["expected_answer"] or "").strip().lower()
                    passed = None
                    if question["knockout"] and expected:
                        normalized = answer.lower()
                        passed = 1 if (expected in normalized or normalized in expected) else 0
                    conn.execute(
                        """
                        insert into application_answers (
                          application_id, question_id, question, answer, knockout_passed, created_at
                        ) values (?, ?, ?, ?, ?, ?)
                        """,
                        (application_id, question["id"], question["question"], answer, passed, now),
                    )
                conn.execute(
                    """
                    insert into application_stage_history (
                      application_id, from_stage_id, to_stage_id, moved_by_user_id, comment, created_at
                    ) values (?, null, ?, null, ?, ?)
                    """,
                    (application_id, stage["id"] if stage else None, "Candidatura recebida e analisada pelo ATS inicial.", now),
                )
                detail = job_detail(conn, job_id)
            self.send_json(201, {"application_id": application_id, "analysis": analysis, "job": detail})
            return

        if path.startswith("/api/applications/") and path.endswith("/move"):
            parts = path.strip("/").split("/")
            try:
                application_id = int(parts[2])
                stage_id = int(body.get("stage_id"))
            except (IndexError, ValueError, TypeError):
                self.send_json(400, {"error": "Informe a candidatura e a fase de destino."})
                return
            now = iso(utc_now())
            with connect() as conn:
                application = conn.execute("select * from applications where id = ?", (application_id,)).fetchone()
                stage = conn.execute("select * from job_stages where id = ?", (stage_id,)).fetchone()
                if not application or not stage:
                    self.send_json(404, {"error": "Candidatura ou fase não encontrada."})
                    return
                conn.execute(
                    "update applications set current_stage_id = ?, updated_at = ? where id = ?",
                    (stage_id, now, application_id),
                )
                conn.execute(
                    """
                    insert into application_stage_history (
                      application_id, from_stage_id, to_stage_id, moved_by_user_id, comment, created_at
                    ) values (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        application_id,
                        application["current_stage_id"],
                        stage_id,
                        body.get("user_id"),
                        body.get("comment") or "",
                        now,
                    ),
                )
                detail = job_detail(conn, application["job_id"])
            self.send_json(200, detail or {})
            return

        if path.startswith("/api/applications/") and path.endswith("/comments"):
            parts = path.strip("/").split("/")
            try:
                application_id = int(parts[2])
            except (IndexError, ValueError):
                self.send_json(400, {"error": "Candidatura inválida."})
                return
            comment = (body.get("comment") or "").strip()
            if not comment:
                self.send_json(400, {"error": "Escreva um comentário interno."})
                return
            now = iso(utc_now())
            with connect() as conn:
                application = conn.execute("select * from applications where id = ?", (application_id,)).fetchone()
                if not application:
                    self.send_json(404, {"error": "Candidatura não encontrada."})
                    return
                conn.execute(
                    "insert into application_comments (application_id, user_id, comment, created_at) values (?, ?, ?, ?)",
                    (application_id, body.get("user_id"), comment, now),
                )
                detail = job_detail(conn, application["job_id"])
            self.send_json(201, detail or {})
            return

        if path.startswith("/api/employees/") and path.endswith("/invite"):
            parts = path.strip("/").split("/")
            user_id = int(parts[2])
            token = secrets.token_urlsafe(12)
            expires = iso(utc_now() + timedelta(hours=12))
            now = iso(utc_now())
            with connect() as conn:
                row = find_user_by_id(conn, user_id)
                if not row:
                    self.send_json(404, {"error": "Colaborador não encontrado."})
                    return
                conn.execute(
                    "update users set invite_token = ?, invite_expires_at = ?, invite_used_at = null, updated_at = ? where id = ?",
                    (token, expires, now, user_id),
                )
                row = find_user_by_id(conn, user_id)
            self.send_json(200, {"employee": public_user(row)})
            return

        if path.startswith("/api/invites/") and path.endswith("/complete"):
            token = path.strip("/").split("/")[2]
            password = body.get("password") or ""
            profile = body.get("profile") or {}
            if len(password) < 4:
                self.send_json(400, {"error": "A senha precisa ter pelo menos 4 caracteres para este teste local."})
                return
            with connect() as conn:
                row = find_invite(conn, token)
                if not row:
                    self.send_json(404, {"error": "Link não encontrado."})
                    return
                user = public_user(row)
                if user["invite_status"] == "expirado":
                    self.send_json(410, {"error": "Este link expirou. Peça um novo link ao RH."})
                    return
                if user["invite_status"] == "usado":
                    self.send_json(409, {"error": "Este link já foi usado."})
                    return
                now = iso(utc_now())
                conn.execute(
                    """
                    update users
                    set password_hash = ?, preferred_name = ?, profile_json = ?, is_active = 1,
                        must_complete_profile = 0, invite_used_at = ?, updated_at = ?
                    where id = ?
                    """,
                    (
                        hash_password(password),
                        profile.get("nickname") or profile.get("preferred_name") or row["preferred_name"],
                        json.dumps(profile, ensure_ascii=False),
                        now,
                        now,
                        row["id"],
                    ),
                )
                row = find_user_by_id(conn, row["id"])
            self.send_json(200, {"user": public_user(row)})
            return

        if path == "/api/dev/reset":
            backup = None
            if DB_PATH.exists():
                backup = DB_PATH.with_suffix(".backup.sqlite")
                shutil.copyfile(DB_PATH, backup)
            init_db(reset=True)
            self.send_json(200, {"ok": True, "database": str(DB_PATH), "backup": str(backup) if backup else ""})
            return

        self.send_json(404, {"error": "Não encontrado."})

    def do_DELETE(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        if path.startswith("/api/jobs/"):
            try:
                job_id = int(path.strip("/").split("/")[2])
            except (IndexError, ValueError):
                self.send_json(400, {"error": "Vaga inválida."})
                return
            with connect() as conn:
                job = conn.execute("select * from jobs where id = ?", (job_id,)).fetchone()
                if not job:
                    self.send_json(404, {"error": "Vaga não encontrada."})
                    return
                application_rows = conn.execute("select id from applications where job_id = ?", (job_id,)).fetchall()
                application_ids = [row["id"] for row in application_rows]
                if application_ids:
                    placeholders = ",".join("?" for _ in application_ids)
                    conn.execute(f"delete from application_comments where application_id in ({placeholders})", application_ids)
                    conn.execute(f"delete from application_stage_history where application_id in ({placeholders})", application_ids)
                    conn.execute(f"delete from application_answers where application_id in ({placeholders})", application_ids)
                    conn.execute(f"delete from applications where id in ({placeholders})", application_ids)
                conn.execute("delete from job_questions where job_id = ?", (job_id,))
                conn.execute("delete from job_stages where job_id = ?", (job_id,))
                conn.execute("delete from jobs where id = ?", (job_id,))
            self.send_json(200, {"ok": True})
            return

        self.send_json(404, {"error": "Não encontrado."})


def main() -> None:
    parser = argparse.ArgumentParser(description="Servidor local do Nvoip People Hub.")
    parser.add_argument("--reset", action="store_true", help="zera o banco local antes de iniciar")
    parser.add_argument("--port", type=int, default=5173)
    args = parser.parse_args()

    init_db(reset=args.reset)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), PeopleHubHandler)
    print(f"Nvoip People Hub local: http://localhost:{args.port}")
    print(f"Banco local: {DB_PATH}")
    print("Admin local: guilherme.faria@nvoip.com.br sem senha")
    server.serve_forever()


if __name__ == "__main__":
    main()
