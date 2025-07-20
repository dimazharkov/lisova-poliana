from app.core.contracts.config_provider_contract import ConfigProviderContract
from app.core.contracts.stat_evaluator_contract import StatEvaluatorContract
from app.core.use_cases.experiments.base.groupped_effect import GroupedEffectExperimentUseCase


class ControlTreatmentExperimentUseCase(GroupedEffectExperimentUseCase):
    def __init__(
            self,
            stat_evaluator: StatEvaluatorContract,
            experiment_config: ConfigProviderContract
    ):
        super().__init__(
            stat_evaluator,
            experiment_config=experiment_config,
            experiment_hue="treatment"
        )



