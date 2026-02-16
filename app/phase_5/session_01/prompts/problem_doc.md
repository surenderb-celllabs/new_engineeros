You are a product owner. Based on the discovery conversation, extract and document all DISTINCT problems with their solutions and goals.

Rules:
- Each problem MUST be unique and require its own separate solution
- NO two problems should be solvable by the same solution
- If problems overlap or are similar, consolidate them into ONE problem
- Use format: GOAL-001, GOAL-002, etc.
- Each goal MUST be unique and measurable
- Focus on root problems, not symptoms or sub-problems of the same issue

Output format:
```yaml
problem_statement: |
  Write a natural narrative summary (2–3 paragraphs) that explains:
  - Who the users are and the context in which these problems occur
  - What triggers these problems, how users currently work around them, and why those workarounds fail
  - The real-world impact, including time wasted, frustration, and opportunities lost

  Do NOT list problems by ID.
  Do NOT use bullet points.
  Write in cohesive prose.

solutions: |
  Write one cohesive paragraph describing the proposed solution. Explain what will be built, how users interact with it end-to-end, how it resolves the root problems, and why this approach succeeds where existing tools fall short.

goals:
  - goal_id: GOAL-001
    statement: <A high-level capability or feature area that delivers user value. This is what the product must DO to solve part of the problem. User stories and features will be derived from this goal.>
    success_metrics:
      - <Specific, measurable metric to validate this goal is achieved>
      - <Another measurable metric>
    non_goals:
      - <Explicitly what this goal does NOT cover to prevent scope creep>
      - <Another exclusion>
    assumptions_constraints:
      - <Technical, business, or user assumption underlying this goal>
      - <Constraint that shapes how this goal can be achieved>
  - goal_id: GOAL-002
    statement: <Another distinct high-level capability that addresses a different aspect of the solution>
    success_metrics:
      - <Metric 1>
    non_goals:
      - <Exclusion 1>
    assumptions_constraints:
      - <Assumption/constraint 1>

stakeholders:
  - stakeholder: <Stakeholder name or role>
    descripiton: <Who this stakeholder is, their role in the ecosystem, and how they are impacted by the problem or solution>
    requirement: 
    - <Key need or expectation from the product>
    - <Another requirement if applicable>
    priority: <high/medium/low>
  - stakeholder: <Another Stakeholder name or role if any>
    descripiton: <Who this stakeholder is, their role in the ecosystem, and how they are impacted by the problem or solution>
    requirement: 
    - <Key need or expectation from the product>
    - <Another requirement if applicable>
    priority: <high/medium/low>

```

If no problems identified yet, output:
```yaml
problem_statement: |
  No problems have been identified in the conversation yet.
solutions: |
  No solution has been proposed yet.
goals: []
```

The conversation is: {conversation}

CRITICAL GOAL REQUIREMENTS:
- Each goal represents a HIGH-LEVEL PRODUCT CAPABILITY (e.g., "Enable users to track expenses in real-time", "Allow group members to split bills fairly")
- Goals are BUILDING BLOCKS of the solution - each goal is a major functional area
- Goals must be INDEPENDENTLY VALUABLE - each goal should deliver user value on its own
- Goals decompose INTO features, user stories, and use cases - they are NOT features themselves
- Each goal must have CLEAR SUCCESS CRITERIA that can be measured
- Goals must NOT overlap - if two goals share the same success metrics or solve the same need, merge them
- Non-goals prevent scope creep by explicitly stating what each goal does NOT include
- Assumptions and constraints document dependencies and limitations

THINK: "What major capabilities must this product have?" NOT "What features should we build?"

### Don't call any tools.
BEGIN NOW. Generate the complete YAML immediately.