#!/bin/python3

DEBUG = False
DEBUG_TEST_LINE_COUNT = 2

class SolutionCandidate:
  def __init__(self, input, ruleStack):
    self.input = input
    self.ruleStack = ruleStack

class GrammarParseNode:
  def __init__(self, line):
    self.line = line.strip()
    self.parseGraph = self.buildParseGraph()

  def buildParseGraph(self):
    raise NotImplementedError()

  def tryMatch(self, input, ruleStack, ruleDictionary):
    raise NotImplementedError()

  # handle the now required potential-match list inputs and outputs to play nice with the existing match functions
  def tryMatchWrapper(self, solutionCandidates, ruleDictionary):
    processedSolutionCandidates = []
    if not type(solutionCandidates) == list:
      solutionCandidates = [solutionCandidates]
    for candidate in solutionCandidates:
      (doesMatch, newSolutionCandidates) = self.tryMatch(candidate.input, candidate.ruleStack.copy(), ruleDictionary)
      if doesMatch:
        if type(newSolutionCandidates) == list:
          processedSolutionCandidates.extend(newSolutionCandidates)
        else:
          processedSolutionCandidates.append(newSolutionCandidates)

    doesMatch = len(processedSolutionCandidates) > 0
    return (doesMatch, processedSolutionCandidates if doesMatch else solutionCandidates)

class LiteralParseNode(GrammarParseNode):
  def buildParseGraph(self):
    return None

  def tryMatch(self, input, ruleStack, ruleDictionary):
    processedInput = input
    if DEBUG:
      print(f"attempt to match '{self.line}' into '{processedInput}'")
    doesMatch = processedInput.startswith(self.line)

    # if there is a match, consume input
    if doesMatch:
      if DEBUG:
        print(f"matched literal '{self.line}'")
      processedInput = processedInput.replace(self.line, "", 1)

    if DEBUG and doesMatch:
      print(f"return new token stream: '{processedInput}'")

    # if a token got processed we reset the rule Stack - literally any rule can try to consume the next token now
    newSolutionCandidate = SolutionCandidate(processedInput, [] if doesMatch else ruleStack)
    return (doesMatch, newSolutionCandidate)

class RuleReferenceParseNode(GrammarParseNode):
  def buildParseGraph(self):
    return None

  def tryMatch(self, input, ruleStack, ruleDictionary):
    ruleToMatch = ruleDictionary[self.line]

    # if this rule is already being applied to the current token we skip to avoid recursion
    if self.line in ruleStack:
      return (False, ruleStack, input)

    ruleStack.append(self.line)

    # if DEBUG:
    #   print(f"reference rule {self.line} for further parsing")
    (doesMatch, newSolutionCandidates) = ruleToMatch.tryMatch(input, ruleStack, ruleDictionary)

    return (doesMatch, newSolutionCandidates)

class SequentialParseNode(GrammarParseNode):
  def buildParseGraph(self):
    sequenceNodes = []
    sequenceTokens = self.line.split(" ")
    for sequenceToken in sequenceTokens:
      if sequenceToken.startswith("\""):
        sequenceNodes.append(LiteralParseNode(sequenceToken.replace("\"", "")))
      else:
        sequenceNodes.append(RuleReferenceParseNode(sequenceToken))
    return sequenceNodes

  def tryMatch(self, input, ruleStack, ruleDictionary):
    processedInput = input

    if DEBUG:
      print(f"matching sequence '{self.line}' with input '{input}'")
    currentSolutionCandidate = SolutionCandidate(input, ruleStack.copy())
    for parseNodeToMatch in self.parseGraph:
      (doesMatch, currentSolutionCandidate) = parseNodeToMatch.tryMatchWrapper(currentSolutionCandidate, ruleDictionary)

      if not doesMatch:
        break

    return (doesMatch, currentSolutionCandidate if doesMatch else SolutionCandidate(input, ruleStack))

class OptionParseNode(GrammarParseNode):
  def buildParseGraph(self):
    optionNodes = []
    optionLines = self.line.split("|")
    for optionLine in optionLines:
      optionNodes.append(SequentialParseNode(optionLine))
    return optionNodes

  def tryMatch(self, input, ruleStack, ruleDictionary):
    # now that we have loops parsing options becomes a bit more difficult, now we have to handle multiple solution candidates that
    # might match depending on the structure of other rules
    # we also have to make sure we're avoiding loops by keeping track of what rules are being already applied on the current token
    potentialMatches = []
    for optionParseNode in self.parseGraph:
      currentSolutionCandidate = SolutionCandidate(input, ruleStack.copy())
      (doesMatch, newSolutioncandidate) = optionParseNode.tryMatchWrapper(currentSolutionCandidate, ruleDictionary)

      if doesMatch:
        # if DEBUG:
        #   print(f"option '{optionParseNode.line}' has found matches")
        if type(newSolutioncandidate) == list:
          potentialMatches.extend(newSolutioncandidate)
        else:
          potentialMatches.append(newSolutioncandidate)

    doesMatch = len(potentialMatches) > 0
    return (doesMatch, potentialMatches if doesMatch else [SolutionCandidate(input, ruleStack)])


class GrammarRule:
  def __init__(self, name, line):
    self.name = name
    self.line = line
    self.parseGraph = self.buildParseGraph()

  def buildParseGraph(self):
    return OptionParseNode(self.line)

  def tryMatch(self, input, ruleStack, ruleDictionary):
    # if DEBUG:
    #   print(f"matching grammar rule {self.name} with input '{input}'")
    return self.parseGraph.tryMatchWrapper(SolutionCandidate(input, ruleStack), ruleDictionary)

f = open("input.txt", "r")
line = f.readline()
grammarLines = []
while line.strip() != "":
  grammarLines.append(line)
  line = f.readline()

line = f.readline()
testLines = []
while line:
  testLines.append(line.strip())
  line = f.readline()

grammarDictionary = {}
for grammarLine in grammarLines:
  splitLine = grammarLine.split(": ")
  ruleName = splitLine[0]
  ruleDefinition = splitLine[1]
  grammarDictionary[ruleName] = GrammarRule(ruleName, ruleDefinition)

# Overwrite rules as per problem definition!
grammarDictionary["8"] = GrammarRule("8", "42 | 42 8")
grammarDictionary["11"] = GrammarRule("11", "42 31 | 42 11 31")

count = 0
debugTestLineCounter = 1
for testLine in testLines:
  if DEBUG:
    print(f"line to test: {testLine}")

  (doesMatch, solutionCandidates) = grammarDictionary["0"].tryMatch(testLine, ["0"], grammarDictionary)
  # if it matches and all input was processed we have a hit
  if doesMatch:
    for candidate in solutionCandidates:
      if len(candidate.input) == 0:
        print(f"matched line {testLine}")
        count += 1
        break
  
  if DEBUG:
    print("==================")

  if DEBUG and debugTestLineCounter == DEBUG_TEST_LINE_COUNT:
    break
  debugTestLineCounter += 1

print(count)
