# Diagram Generation

### Sequence Diagram

Uses [PlantUML](https://plantuml.com/)

```
java -jar plantuml.jar gophish_sequence.plantuml -svg
```

### Dependency Diagram

Uses [mermaid](https://mermaid-js.github.io/mermaid/#/flowchart?id=flowcharts-basic-syntax)

```
npm install @mermaid-js/mermaid-cli
node_modules/.bin/mmdc -i gophish_dependency.mmd -o gophish_dependency.svg

# https://github.com/mermaid-js/mermaid-cli/issues/110
sed -i 's#<br>#<br/>#g' gophish_dependency.svg
```

### Data Diagram

Uses [PlantUML](https://plantuml.com/)

```
java -jar plantuml.jar gophish_data.plantuml -svg
```
