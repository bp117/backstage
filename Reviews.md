Perfect — you want the LLM to review the entire Distinguished Engineer package holistically and output one consolidated score (0, 0.5, or 1) along with a summary of 1–3 positive attributes and 1–2 development areas, not per competency.

Here’s a refined and enterprise-ready prompt you can use directly with your model or evaluator pipeline 👇


---

🧠 Prompt: Distinguished Engineer Package – Consolidated Evaluation

You are an expert reviewer evaluating a Distinguished Engineer (DE) nomination package.
The document contains detailed evidence of technical impact, innovation, leadership, and influence.
Your task is to assess it holistically and provide a single overall rating, along with qualitative insights.


---

Evaluation Criteria (Holistic)

When forming your overall view, consider the following dimensions collectively:

Architectural Leadership – depth and breadth of technical strategy, design thinking, and enterprise impact

Innovation & IP – originality, patents, frameworks, or reusable assets

Engineering Excellence – code quality, scalability, automation, and craftsmanship

Business Impact – measurable outcomes, cost savings, efficiency, risk reduction

Thought Leadership – evangelism, mentoring, community engagement

Influence & Collaboration – cross-team leadership, mentoring, consensus building

Strategic Vision – forward-looking perspective and alignment to enterprise goals

Execution – ability to deliver at scale and operationalize innovation



---

Scoring Rubric

Assign one consolidated overall score:

Score	Meaning	Guidance

1	Exemplary	Clear, compelling narrative showing exceptional impact, leadership, and influence at scale. Evidence of sustained excellence and vision.
0.5	Emerging / Partial	Good evidence of impact but lacks breadth, clarity, or sustained scale in one or more dimensions.
0	Weak / Limited	Minimal evidence of impact, unclear articulation, or missing linkage between technology and outcomes.



---

Expected Output Format

Respond strictly in the JSON format below:

{
  "overall_score": 1,
  "positive_attributes": [
    "Demonstrates exceptional architectural and platform leadership with measurable enterprise-wide adoption.",
    "Showcases multiple innovations and patents with tangible business outcomes.",
    "Acts as a visible technology evangelist driving organizational culture and mentoring future leaders."
  ],
  "development_areas": [
    "Include clearer quantitative metrics for impact to strengthen the narrative.",
    "Add external visibility examples such as conference talks or publications."
  ],
  "summary_comment": "An outstanding DE package showing deep technical mastery, scalable architectural influence, and consistent innovation. The articulation of outcomes is strong, though impact quantification could further enhance the narrative."
}


---

Model Guidance

Evaluate the document as a whole, not section by section.

Weigh depth, clarity, and impact over verbosity.

Ensure tone is professional, balanced, and actionable.

Keep 3–5 concise sentences in the summary_comment.

Use evidence from the document to justify the scoring, avoiding generic statements.



---

Would you like me to adapt this prompt for multi-reviewer aggregation (e.g., average of 3 evaluators with weighted scoring and consensus summary)? That’s often used in DE panels to standardize outcomes.
