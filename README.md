# IproK-Web: Web Application for Project Data Management

This repository contains the code for **IproK-Web**, a web-based application designed to serve as the primary user interface for the **IproK (Integrated Project Knowledge) Ontology**.

The core purpose of this application is to empower non-technical users—such as Project Managers—to perform complex project management tasks (e.g., creating projects, defining schedules, assigning resources) without needing to write SPARQL queries or directly manipulate ontology files.

## 🚀 [Live Demo](https://iprok-web.streamlit.app/)

A demonstration of the web application's features and workflow is available on LinkedIn:

**[Watch the Demo Here](https://www.linkedin.com/posts/venkatesh-kone-66149a13b_recent-projectmanagement-ontology-activity-7283045841710301185-bxEi?utm_source=share&utm_medium=member_desktop&rcm=ACoAACIQwCkBp2QaEf7S_hwzh8Tlk-d4C5BjW_w)**

## 🎯 Role in the IproK Ecosystem

This application is a critical component of the larger IproK research project:

* **`Iprok-web` (This Repo):** Acts as the **data entry and visualization** layer. It's the "front-end" where Project Managers create and manage their project data, which *populates* the IproK knowledge graph.
* **`Semantic-BIM-Workflow` (Other Repo):** Acts as the **data integration and export** layer. It *consumes* the knowledge graph populated by this web app and integrates it with BIM/IFC models.

In short: **This app creates the project data, and the `Semantic-BIM-Workflow` project links that data to the 3D model.**

## ✨ Key Features

* **Project Creation:** Initialize new construction projects within the knowledge graph.
* **WBS Management:** Create, update, and delete Work Breakdown Structure (WBS) elements, including tasks, schedules, and dependencies.
* **Resource & Cost:** Assign resources (labor, materials, equipment) and costs to specific tasks.
* **Ontology-Driven:** Uses the IproK ontology as its backend, ensuring all data is semantically structured, validated, and consistent.
* **Interactive Visualization:** (e.g., Gantt charts, cost dashboards) Provides visual feedback on project status based on the live graph data.
* **User-Friendly UI:** Built with Streamlit for a simple, intuitive, and data-centric user experience.

## 🛠️ Technology Stack

* **Core Language:** Python
* **Web Framework:** **Streamlit** (for the rapid development of the data-centric user interface)
* **Ontology Interaction:** **Owlready2** (for programmatically manipulating the IproK ontology)
* **Graph Operations:** **NetworkX** (for handling and analyzing task dependencies and graph structures)
* **Data Visualization:** **Plotly**, **Matplotlib** (for generating interactive charts and dashboards)
* **Data Handling:** Pandas, NumPy

## 🚀 Installation and Usage

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/VenkateshKone-1/Iprok-web.git](https://github.com/VenkateshKone-1/Iprok-web.git)
    cd Iprok-web
    ```

2.  **Create a virtual environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Streamlit app:**
    ```bash
    streamlit run app.py
    ```

5.  Open your browser and navigate to `http://localhost:8501`.
