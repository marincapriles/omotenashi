# Omotenashi PRD v0.2

## Overview

Omotenashi is a AI agent platform that allows customers to build, configure and deploy teams agents to perform business workflows

## Requirements

### Agents

- Agents are instantiated with a set of beliefs, desires and intentions (BDI) that guide their behavior
- Customers can select the agent BDI profile from a set of templates
- Agents can evolve their BDI profile over time based on their experiences and customer feedback
- Agents are stateful and have memory of customer interactions, learnings and to dos
- Agents have a set of tools that they can use to perform tasks

### Teams

- Multiple agents can belong to a team
- Teams come with a predefined assemble of agents and BDI profiles
- Agents on a team have shared memory and are aware of each other's state
- Agents can communicate with each other using a shared communication channel
- Agents make decisions collectively

### Workflows

- Teams perform workflows by coordinating agent's actions with a common goal
- Teams have predefined workflows that they can perform

### Tools

- Tools are functions that agents can call to perform tasks
- Tools available to agent are defined by their BDI profile
- Tools can be retrieving information from a knowledge base, making a modification to a database, calling an external API, etc

### Frameworks

- Use Anthropic API with Claude 3.5 Sonnet to power agents
- Use LangGraph framework to build agentic workflows

### Frontend

- A CLI allows users to interact with the platform and agents

## Prototype v0.1

- Create 1 agent with a Luxury Hospitality Guest Concierge BDI profile
- Base the BDI profile on the concept of Omotenashi, the Japanese art of hospitality
- BDI profile includes 5 tools:
  -- provide property information
  -- provide curated recommendations
  -- book a reservation
  -- book a spa appointment
  -- Modify check-in and check-out times
- Build a CLI that allows users to interact with the agent
- User can talk to the agent
- Agent responds with
  -- message to users
  -- list of tools it used to perform the task
  -- reasoning for its behavior grounded on BDI profile

## Prototype v0.2

- Add Agent 2, the Operations Manager with it sown BDI profile, to work with Agent 1 by communicating with the Property Manager (user)
- Base the BDI profile on the concept of Omotenashi, the Japanese art of hospitality
- BDI profile includes the following tools:
  -- Communicate changes in booking
  -- Resolve escalation
  -- Alert of guest issue
  -- Provide daily update
  -- Provide operational check in
- Agent 1 actions can trigger actions on Agent 2 and vice versa
- Add the following tool to Agent 1: Trigger escalation. This should be used when Agent 1 is unable to resolve the guest need
  with available tools or is unsure what to do.
- Agent 2 should communicate with the Property Manager when
  -- Agent 1 modifies a check in or check out time
  -- Triggers an escalation
- Show Agent 2 responses and tool use on a clearly label section of the repsonse on the CLI

  ## Development Principles

  - Keep it very simple
  - Build each piece of functionality iteratively
  - Riguriously comment your code so I can understand what it does
  - Create a design decisions log so I can understand what assumptions you are making
  - Use this PRD as single source of truth for what to build. Do not build components that are not directly related to this scope
  - This is a research prototype, do not worry about production ready.
