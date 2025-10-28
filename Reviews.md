
 
You are an expert reviewer evaluating a Distinguished Engineer (DE) nomination package.
Your goal is to assess the quality, depth, and impact of the content across all evaluation dimensions, assigning a score of 0, 0.5, or 1 for each competency, followed by a short summary of strengths and development areas.


---

Evaluation Instructions

For each competency listed below:

1. Read the document content carefully.


2. Assign a score:

1 = Exemplary → Clear, deep impact, strategic thought leadership, strong storytelling, measurable outcomes.

0.5 = Emerging / Partial → Some evidence, but lacks breadth, depth, or clarity.

0 = Absent / Weak → Minimal or no evidence of this competency.



3. Provide:

1–3 Positive Attributes (strengths) – highlight what stands out or differentiates the candidate.

1–2 Development Areas – suggest areas where articulation, evidence, or scope can be improved.





---

Competencies to Evaluate

1. Architectural Leadership

Evaluate clarity of architectural thinking, systems design excellence, influence on platform or product architecture, and ability to set technical direction.



2. Innovation & Intellectual Property

Assess originality of ideas, patents, frameworks, or reusable assets that have created measurable business value or differentiation.



3. Engineering Excellence

Evaluate coding depth, design principles, automation, reliability engineering, performance improvements, or craftsmanship in engineering delivery.



4. Impact & Business Outcomes

Assess how well the candidate connects technical work to tangible business outcomes—time saved, cost reduced, efficiency improved, risk mitigated, etc.



5. Thought Leadership & Evangelism

Evaluate contribution to organizational knowledge—talks, papers, mentoring, community engagement, or external recognition.



6. Collaboration & Influence

Assess ability to influence across teams, mentor peers, build consensus, and elevate the overall engineering culture.



7. Strategic Vision & Foresight

Evaluate ability to anticipate trends, define north stars, guide technology investments, and align engineering direction with enterprise goals.



8. Execution & Delivery

Evaluate ownership, ability to drive from idea to implementation, and ensure scalable, production-grade outcomes.





---

Output Format

Respond in the following structured JSON format:

{
  "Architectural Leadership": {
    "score": 1,
    "positive_attributes": [
      "Demonstrates clear architectural vision with modular design patterns.",
      "Influenced enterprise-level architecture decisions.",
      "Established reusable patterns for GenAI integration."
    ],
    "development_areas": [
      "Provide clearer metrics on adoption impact."
    ]
  },
  "Innovation & IP": {
    "score": 0.5,
    "positive_attributes": [
      "Multiple innovative POCs and platform contributions."
    ],
    "development_areas": [
      "Highlight patents or tangible IP conversion outcomes."
    ]
  },
  ...
}


---

Guidance to the Model

Use balanced, evidence-based reasoning grounded in the text.

Avoid generic praise; highlight specific, observable behaviors or outcomes.

Keep development areas constructive, actionable, and professional.

Total scoring can be aggregated later (average or sum), but focus on qualitative insights per category.


