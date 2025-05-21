from owlready2 import get_ontology

def calculate_costs(project_path):
    onto = get_ontology(project_path).load()
    task_costs = []

    for task in onto.Task.instances():
        if task.hasResourcesItem:
            resource_item = task.hasResourcesItem
            budgeted_cost = 0.0
            actual_cost = 0.0
            remaining_cost = 0.0
            at_complete_cost = 0.0
            cost_item = task.hasCostItem
            other_cost = float(cost_item.Expense) if hasattr(cost_item, 'Expense') and cost_item.Expense is not None else 0.0

            for resource in resource_item.hasResources:
                if resource.hasResourceCategory:
                    resource_category = resource.hasResourceCategory
                    base_rate = resource_category.BaseRate_onDate if hasattr(resource_category, 'BaseRate_onDate') else 0.0

                    if hasattr(resource, 'BudgetedUnits') and resource.BudgetedUnits is not None and base_rate is not None:
                        budgeted_cost += resource.BudgetedUnits * base_rate
                    if hasattr(resource, 'ActualUnits') and resource.ActualUnits is not None and base_rate is not None:
                        actual_cost += resource.ActualUnits * base_rate
                    if hasattr(resource, 'RemainingUnits') and resource.RemainingUnits is not None and base_rate is not None:
                        remaining_cost += resource.RemainingUnits * base_rate
                    if hasattr(resource, 'AtCompleteUnits') and resource.AtCompleteUnits is not None and base_rate is not None:
                        at_complete_cost += resource.AtCompleteUnits * base_rate

            # Save calculated costs in the ontology
            cost_item.BudgetedCost = budgeted_cost + other_cost
            cost_item.ActualCost = actual_cost + other_cost
            cost_item.RemainingCost = remaining_cost
            cost_item.AtCompleteCost = at_complete_cost + other_cost

            task_costs.append({
                'TaskId': task.Id,
                'BudgetedCost': budgeted_cost + other_cost,
                'ActualCost': actual_cost + other_cost,
                'RemainingCost': remaining_cost,
                'AtCompleteCost': at_complete_cost + other_cost,
            })

    try:
        onto.save(project_path, format="rdfxml")
    except Exception as e:
        print(f"Failed to save ontology file: {e}")

    try:
        onto.destroy()
    except Exception as e:
        print(f"Failed to destroy ontology: {e}")

    return task_costs

def calculate_resource_costs(project_path):
    onto = get_ontology(project_path).load()
    resource_costs = []

    for task in onto.Task.instances():
        if task.hasResourcesItem:
            resource_item = task.hasResourcesItem
            cost_item = task.hasCostItem
            labor_cost = 0.0
            material_cost = 0.0
            equipment_cost = 0.0
            
            other_cost = float(cost_item.Expense) if hasattr(cost_item, 'Expense') and cost_item.Expense is not None else 0.0

            for resource in resource_item.hasResources:
                if resource.hasResourceCategory:
                    resource_category = resource.hasResourceCategory
                    base_rate = resource_category.BaseRate_onDate if hasattr(resource_category, 'BaseRate_onDate') else 0.0
                    actual_cost = 0.0

                    if hasattr(resource, 'BudgetedUnits') and resource.BudgetedUnits is not None and base_rate is not None:
                        actual_cost += resource.BudgetedUnits * base_rate

                    if isinstance(resource_category, onto.LaborResource):
                        labor_cost += actual_cost
                    elif isinstance(resource_category, onto.MaterialResource):
                        material_cost += actual_cost
                    elif isinstance(resource_category, onto.EquipmentResource):
                        equipment_cost += actual_cost
                    else:
                        other_cost += actual_cost

            resource_costs.append({
                'TaskId': task.Id,
                'LaborCost': labor_cost,
                'MaterialCost': material_cost,
                'EquipmentCost': equipment_cost,
                'OtherCost': other_cost
            })

    try:
        onto.destroy()
    except Exception as e:
        print(f"Failed to destroy ontology: {e}")

    return resource_costs

def calculate_resource_category_costs(project_path):
    onto = get_ontology(project_path).load()
    resource_category_costs = {}

    for task in onto.Task.instances():
        if task.hasResourcesItem:
            resource_item = task.hasResourcesItem
            cost_item = task.hasCostItem
            other_cost = float(cost_item.Expense) if hasattr(cost_item, 'Expense') and cost_item.Expense is not None else 0.0

            for resource in resource_item.hasResources:
                if resource.hasResourceCategory:
                    resource_category = resource.hasResourceCategory
                    base_rate = resource_category.BaseRate_onDate if hasattr(resource_category, 'BaseRate_onDate') else 0.0
                    budgeted_units = resource.BudgetedUnits if hasattr(resource, 'BudgetedUnits') and resource.BudgetedUnits is not None else 0.0

                    if resource_category.name not in resource_category_costs:
                        resource_category_costs[resource_category.name] = 0.0
                    if budgeted_units is not None and base_rate is not None:
                        resource_category_costs[resource_category.name] += budgeted_units * base_rate

            if 'Other' not in resource_category_costs:
                resource_category_costs['Other'] = 0.0
            resource_category_costs['Other'] += other_cost

    try:
        onto.destroy()
    except Exception as e:
        print(f"Failed to destroy ontology: {e}")

    return resource_category_costs

def calculate_resource_type_costs(project_path):
    onto = get_ontology(project_path).load()
    resource_type_costs = {
        'Labor': 0.0,
        'Material': 0.0,
        'Equipment': 0.0,
        'Other': 0.0
    }

    for task in onto.Task.instances():
        if task.hasResourcesItem:
            resource_item = task.hasResourcesItem
            cost_item = task.hasCostItem
            other_cost = float(cost_item.Expense) if hasattr(cost_item, 'Expense') and cost_item.Expense is not None else 0.0

            for resource in resource_item.hasResources:
                if resource.hasResourceCategory:
                    resource_category = resource.hasResourceCategory
                    base_rate = resource_category.BaseRate_onDate if hasattr(resource_category, 'BaseRate_onDate') else 0.0
                    budgeted_units = resource.BudgetedUnits if hasattr(resource, 'BudgetedUnits') and resource.BudgetedUnits is not None else 0.0
                    total_cost = budgeted_units * base_rate if budgeted_units is not None and base_rate is not None else 0.0

                    if isinstance(resource_category, onto.LaborResource):
                        resource_type_costs['Labor'] += total_cost
                    elif isinstance(resource_category, onto.MaterialResource):
                        resource_type_costs['Material'] += total_cost
                    elif isinstance(resource_category, onto.EquipmentResource):
                        resource_type_costs['Equipment'] += total_cost
                    else:
                        resource_type_costs['Other'] += total_cost

            resource_type_costs['Other'] += other_cost

    try:
        onto.destroy()
    except Exception as e:
        print(f"Failed to destroy ontology: {e}")

    return resource_type_costs

