import streamlit as st
import json
import operator

# Mapping string operators from JSON to Python's operator module
ops = {
    ">=": operator.ge,
    "<=": operator.le,
    "<": operator.lt,
    ">": operator.gt,
    "==": operator.eq,
    "!=": operator.ne
}

# The EXACT JSON rules required by the lab, in the exact original order
default_rules = """[
  {
    "name": "Top merit candidate",
    "priority": 100,
    "conditions": [
      ["cgpa", ">=", 3.7],
      ["co_curricular_score", ">=", 80],
      ["family_income", "<=", 8000],
      ["disciplinary_actions", "==", 0]
    ],
    "action": {
      "decision": "AWARD FULL",
      "reason": "Excellent academic & co-curricular performance, with acceptable need"
    }
  },
  {
    "name": "Good candidate partial scholarship",
    "priority": 80,
    "conditions": [
      ["cgpa", ">=", 3.3],
      ["co_curricular_score", ">=", 60],
      ["family_income", "<=", 12000],
      ["disciplinary_actions", "<=", 1]
    ],
    "action": {
      "decision": "AWARD PARTIAL",
      "reason": "Good academic & involvement record with moderate need"
    }
  },
  {
    "name": "Need-based review",
    "priority": 70,
    "conditions": [
      ["cgpa", ">=", 2.5],
      ["family_income", "<=", 4000]
    ],
    "action": {
      "decision": "REVIEW",
      "reason": "High need but borderline academic score"
    }
  },
  {
    "name": "Low CGPA not eligible",
    "priority": 95,
    "conditions": [
      ["cgpa", "<", 2.5]
    ],
    "action": {
      "decision": "REJECT",
      "reason": "CGPA below minimum scholarship requirement"
    }
  },
  {
    "name": "Serious disciplinary record",
    "priority": 90,
    "conditions": [
      ["disciplinary_actions", ">=", 2]
    ],
    "action": {
      "decision": "REJECT",
      "reason": "Too many disciplinary records"
    }
  }
]"""

def evaluate_rules(facts, rules):
    # Sort rules by priority descending (highest priority evaluated first)
    sorted_rules = sorted(rules, key=lambda x: x["priority"], reverse=True)
    
    for rule in sorted_rules:
        conditions_met = True
        for condition in rule["conditions"]:
            fact_name, op_str, value = condition
            
            # If the fact isn't provided, the condition fails
            if fact_name not in facts:
                conditions_met = False
                break
            
            # Evaluate the condition
            fact_value = facts[fact_name]
            if not ops[op_str](fact_value, value):
                conditions_met = False
                break
        
        # If all conditions for this rule are met, trigger the action
        if conditions_met:
            return rule["name"], rule["action"]
            
    return "No Match", {"decision": "PENDING", "reason": "No specific rules were triggered by these facts."}

# --- Streamlit UI ---
st.set_page_config(page_title="Scholarship Advisory Rule Engine", layout="wide")
st.title("🎓 Scholarship Advisory Rule-Based System")
st.markdown("This system uses a rule engine to evaluate scholarship applications based on a transparent set of JSON rules.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Applicant Facts")
    cgpa = st.number_input("Cumulative GPA (CGPA)", min_value=0.0, max_value=4.0, value=3.5, step=0.01)
    family_income = st.number_input("Monthly Family Income (RM)", min_value=0, value=5000, step=100)
    co_curricular_score = st.number_input("Co-curricular Involvement Score (0-100)", min_value=0, max_value=100, value=75, step=1)
    disciplinary_actions = st.number_input("Number of Disciplinary Actions", min_value=0, value=0, step=1)
    
    facts = {
        "cgpa": cgpa,
        "family_income": family_income,
        "co_curricular_score": co_curricular_score,
        "disciplinary_actions": disciplinary_actions
    }
    
    st.write("**Current Facts Dictionary:**")
    st.json(facts)

with col2:
    st.subheader("2. Rule Editor (JSON)")
    rules_input = st.text_area("Edit Scholarship Rules", value=default_rules, height=350)

st.divider()

# --- Evaluation ---
if st.button("Evaluate Application", type="primary", use_container_width=True):
    try:
        rules = json.loads(rules_input)
        rule_name, result = evaluate_rules(facts, rules)
        
        st.subheader("Evaluation Result")
        
        if result["decision"] == "AWARD FULL":
            st.success(f"**Decision:** {result['decision']}")
        elif result["decision"] == "AWARD PARTIAL" or result["decision"] == "REVIEW":
            st.warning(f"**Decision:** {result['decision']}")
        else:
            st.error(f"**Decision:** {result['decision']}")
            
        st.info(f"**Reason:** {result['reason']}")
        st.caption(f"Triggered by rule: '{rule_name}'")
        
    except json.JSONDecodeError:
        st.error("Invalid JSON format in the Rule Editor. Please check your syntax.")
    except Exception as e:
        st.error(f"An error occurred during evaluation: {e}")