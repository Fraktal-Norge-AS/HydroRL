from server.model import Agent
from server.model import StepValue, StepDatum, ReportDatum, ReportValue, EvaluationEpisode
from datetime import datetime as dt
from hps.rl.logging.report_name import filter_report_columns


class DbLogger:
    def __init__(self, session, agent_id, project_run_id, log_type, plot_type, log_steps=True):
        self.session = session
        self.agent_id = agent_id
        self.project_run_id = project_run_id
        self.log_type = log_type
        self.plot_type = plot_type
        self.step_series = None
        self.log_steps = log_steps
        self.report_series = {}
        self.reported_steps = []
        self.episode_mapping = {}

    def log_step_series(
        self,
        step,
        eval_env,
        returns,
        sum_return,
        currentbest,
        new_best,
        rewards,
        end_rewards,
        train_metrics,
        train_loss,
        q_value_tuple,
        q_value,
    ):

        now_time = dt.now()
        data = {"Test Return": sum_return, "Best Return": currentbest["eval"]}

        if self.step_series is None:
            self.step_series = {}
            for label, _ in data.items():
                description = label
                seires = StepDatum(
                    AgentId=self.agent_id, StartTime=str(now_time), Description=description, Type=self.log_type
                )
                self.session.add(seires)
                self.step_series[label] = seires

            self.session.commit()
            self.session.flush()

        for label, value in data.items():
            series_value = StepValue(
                TimeStamp=str(now_time),
                Step=step,
                Value=float(value),
                StepSeriesId=self.step_series[label].StepSeriesId,
            )
            self.session.add(series_value)
        self.session.commit()

    def add_report_series(self, step, values, is_best, name, episode_id, time_index=None):

        if time_index is not None:
            start_time = time_index[0]
            end_time = time_index[-1]
        else:
            start_time = dt.now()
            end_time = start_time
            time_index = [start_time] * len(values)

        series_key = name + "_" + str(episode_id)

        if not series_key in self.report_series:
            report = ReportDatum(
                EvaluationEpisodeId=episode_id,
                StartTime=str(start_time),
                EndTime=str(end_time),
                Description=name,
                Type=self.plot_type,
            )
            self.session.add(report)
            self.session.commit()
            self.session.flush()
            self.report_series[series_key] = report.ReportSeriesId

        for i, (key, value) in enumerate(values.items()):
            report_value = ReportValue(
                ReportSeriesId=self.report_series[series_key],
                Index=key,
                TimeStamp=str(time_index[i]),
                Value=value,
                Step=step,
            )
            self.session.add(report_value)

        self.session.commit()

    def log_eval_episode(self, step, episode_name, eval_env):
        if not episode_name in self.episode_mapping:
            desc = str(episode_name)
            eval_episode = EvaluationEpisode(ProjectRunId=self.project_run_id, Description=desc, AgentId=self.agent_id)
            self.session.add(eval_episode)
            self.session.commit()
            self.session.flush()
            self.episode_mapping[episode_name] = eval_episode.EvaluationEpisodeId

        episode_id = self.episode_mapping[episode_name]
        for col in filter_report_columns(eval_env.report_df.columns):
            dictionary = {i: v for i, v in enumerate(eval_env.report_df[col])}
            self.add_report_series(step, dictionary, True, col, episode_id, eval_env.time_indexer.index)

    def log_info(
        self,
        step,
        eval_env,
        returns,
        sum_return,
        currentbest,
        new_best,
        rewards,
        end_rewards,
        train_metrics,
        train_loss,
        q_value_tuple,
        q_value,
    ):
        if step in self.reported_steps:
            return
        self.reported_steps.append(step)

        if self.log_steps:
            self.log_step_series(
                step,
                eval_env,
                returns,
                sum_return,
                currentbest,
                new_best,
                rewards,
                end_rewards,
                train_metrics,
                train_loss,
                q_value_tuple,
                q_value,
            )

    def terminate_series(self, end_time):
        if self.step_series is not None:
            for series in self.step_series.values():
                series.EndTime = end_time
            self.session.commit()
