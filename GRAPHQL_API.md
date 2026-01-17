# GraphQL API Guide

## Quick Start
```bash
# Start GraphQL server
python -m docassemble_dag interview.yaml --serve-graphql

# Server starts at http://localhost:8000/graphql
# GraphiQL IDE available for interactive queries
```

## Example Queries

### Get a single node
```graphql
query {
  node(name: "age") {
    name
    kind
    source
    filePath
    lineNumber
    dependencies {
      name
      kind
    }
  }
}
```

### Find nodes by authority
```graphql
query {
  nodesByAuthority(pattern: "CPLR") {
    name
    authority
    kind
  }
}
```

### Find path between nodes
```graphql
query {
  path(from: "age", to: "eligibility_rule") {
    nodes
    length
  }
}
```

### Get graph statistics
```graphql
query {
  graphStats {
    nodeCount
    edgeCount
    hasCycles
  }
}
```

## Python Client Example
```python
import requests

query = """
query {
  node(name: "age") {
    name
    dependents {
      name
    }
  }
}
"""

response = requests.post(
    "http://localhost:8000/graphql",
    json={"query": query}
)

data = response.json()
print(data["data"]["node"])
```

## JavaScript Client Example
```javascript
const query = `
  query {
    nodesByAuthority(pattern: "CPLR") {
      name
      authority
    }
  }
`;

fetch('http://localhost:8000/graphql', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query })
})
  .then(res => res.json())
  .then(data => console.log(data));
```
