# lisova-poliana
Data Analysis for the Lisova Poliana center

Подготовка.
1. Подготовка источников:
- python main.py extract params --source-path=source/raw_data.json --target-path=source/params.json
- вручную добавить параметрам в группах (много повторяющиеся) названия групп: "Амплітуда P (мкВ)" -> "Амплітуда P (мкВ) — відведення I"
- python main.py extract param-duplicates --source-path=source/params.json --target-path=source/param_duplicates.json
- python main.py extract personal-data --source-path=source/raw_data.json --target-path=source/personal_data.json
---
2. Подготовка контрольных данных:
- python main.py extract data --source-path=source/raw_data.json --target-path=control_data.json --data-key=контроль
- python main.py data prep --source-path=control_data.json --target-path=control_data.json --treatment=0
- python main.py data inspect --source-path=control_data.json --target-path=control_data.json --noizy-feature-path=control_noizy.json
- python main.py data normalize --source-path=control_data.json --target-path=control_norm.json
- python main.py data aggregate --source-path=control_norm.json --target-path=control_norm.json
- python main.py data personalize --source-path=control_norm.json --target-path=control_norm.json --meta-path=source/personal_data.json
--- 
3. Подготовка данных терапии:
- python main.py extract data --source-path=source/raw_data.json --target-path=treatment_data.json --data-key=Дих
- python main.py data prep --source-path=treatment_data.json --target-path=treatment_data.json --treatment=1
- python main.py data inspect --source-path=treatment_data.json --target-path=treatment_data.json --noizy-feature-path=treatment_noizy.json
- python main.py data normalize --source-path=treatment_data.json --target-path=treatment_norm.json
- python main.py data aggregate --source-path=treatment_norm.json --target-path=treatment_norm.json
- python main.py data personalize --source-path=treatment_norm.json --target-path=treatment_norm.json --meta-path=source/personal_data.json
---
4. Подготовка дельт:
- python main.py delta build --source-path=control_data.json --target-path=control_delta.json
- python main.py delta build --source-path=treatment_data.json --target-path=treatment_delta.json
- python main.py delta combine --source-path=control_delta.json --source-path=treatment_delta.json --target-path=delta.json
- python main.py data inspect --source-path=delta.json --target-path=delta.json --noizy-feature-path=delta_noizy.json
- python main.py data normalize --source-path=delta.json --target-path=delta_norm.json
- python main.py data aggregate --source-path=delta_norm.json --target-path=delta_norm.json
- python main.py data personalize --source-path=delta_norm.json --target-path=delta_norm.json --meta-path=source/personal_data.json
---
5. Эксперименты
- python main.py experiment baseline --source-path control_norm.json --source-path treatment_norm.json --target-folder=baseline
- python main.py experiment before-after --source-path control_norm.json --target-folder=before-after/control-3 --experiment=3 --config-path=experiments/before-after-control-3.json
- python main.py experiment before-after --source-path control_norm.json --target-folder=before-after/control-5 --experiment=5 --config-path=experiments/before-after-control-5.json
- python main.py experiment before-after --source-path treatment_norm.json --target-folder=before-after/treatment-3 --experiment=3 --config-path=experiments/before-after-treatment-3.json
- python main.py experiment before-after --source-path treatment_norm.json --target-folder=before-after/treatment-5 --experiment=5 --config-path=experiments/before-after-treatment-5.json
- python main.py experiment control-treatment --source-path delta_norm.json --target-folder=control-treatment/treatment-3 --experiment=3 --config-path=experiments/control-treatment-treatment-3.json
- python main.py experiment control-treatment --source-path delta_norm.json --target-folder=control-treatment/treatment-5 --experiment=5 --config-path=experiments/control-treatment-treatment-5.json

6. Утилиты
- python main.py utils experiment-map-file --source-path=control-treatment/treatment-5 --config-path=utils/experiment-map-file.json
- python main.py utils export-experiment-data --source-path=control-treatment/treatment-5 --config-path=utils/experiment-map-file.json
- python main.py utils export-experiment-data --source-path=control-treatment/treatment-3 --config-path=utils/experiment-map-file.json
- python main.py utils export-experiment-data --source-path=before-after/control-3 --config-path=utils/experiment-map-file.json
- python main.py utils export-experiment-data --source-path=before-after/control-5 --config-path=utils/experiment-map-file.json
- python main.py utils export-experiment-data --source-path=before-after/treatment-3 --config-path=utils/experiment-map-file.json
- python main.py utils export-experiment-data --source-path=before-after/treatment-5 --config-path=utils/experiment-map-file.json



Все пациенты: мужчины и женщины
- сравниваем выборки до терапии: контрольная и дыхательная
- сравниваем контрольную группу: до терапии, после терапии
- сравниваем контрольную группу, 3х: до терапии, после терапии
- сравниваем контрольную группу, 5х: до терапии, после терапии
- сравниваем дыхательную группу: до терапии, после терапии
- сравниваем дельту: контрольная и дыхательная
- сравниваем дельту, 3хв: контрольная и дыхательная
- сравниваем дельту, 5хв: контрольная и дыхательная

Выбранные параметры:
- возможно какие-то выбранные параметры

Основные эксперименты:
- сравнение между группами до терапии
- сравнение внутри группы до терапии и после
- сравнение дельт (после терапии - до терапии) между группами

Характеристики выборки:
- все пациенты
- эксперимент: 3хв, 5хв
- пол: мужчины
- давление: норм, повышенное
- параметры: все, выбранные, каждый из выбранных
- пересечение всех параметров

Отдельный эксперимент:
- наиболее отзывчивые параметры

---
- между группами: 3, 5
- параметры внутри группы: 3, 5
- параметры между группами: 3, 5
- пройтись по результатам, выбрать от weak, но учесть размер выборки
- найти когда в контрольной нет, в терапии есть и между группами есть
- найти параметры, которые лучше всего реагировали: в группе и между
- выделить параметры, которые хорошо реагировали везде

---
в подготовке данных нужно учесть, чтобы группы различались бинарно: 
"repeat" = [0 | 1]
"treatment" = [0 | 1]