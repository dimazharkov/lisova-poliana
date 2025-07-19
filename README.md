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
- python main.py data personalize --source-path=delta_norm.json --target-path=delta_norm.json --meta-path=source/personal_data.json
---
5. Эксперименты
- python main.py experiment baseline --source-path control_norm.json --source-path treatment_norm.json --target-folder=baseline


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