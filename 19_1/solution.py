#!/bin/python3

DEBUG = False
DEBUG_TEST_LINE_COUNT = 1

class GrammarParseNode:
  def __init__(self, line):
    self.line = line.strip()
    self.parseGraph = self.buildParseGraph()

  def buildParseGraph(self):
    raise NotImplementedError()

  def tryMatch(self, input, ruleDictionary):
    raise NotImplementedError()

class LiteralParseNode(GrammarParseNode):
  def buildParseGraph(self):
    return None

  def tryMatch(self, input, ruleDictionary):
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
    return (doesMatch, processedInput)

class RuleReferenceParseNode(GrammarParseNode):
  def buildParseGraph(self):
    return None

  def tryMatch(self, input, ruleDictionary):
    ruleToMatch = ruleDictionary[self.line]
    if DEBUG:
      print(f"reference rule {self.line} for further parsing")
    doesMatch, processedInput = ruleToMatch.tryMatch(input, ruleDictionary)

    return (doesMatch, processedInput)

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

  def tryMatch(self, input, ruleDictionary):
    processedInput = input

    for parseNodeToMatch in self.parseGraph:
      (doesMatch, processedInput) = parseNodeToMatch.tryMatch(processedInput, ruleDictionary)

      if not doesMatch:
        break

    return (doesMatch, processedInput)

class OptionParseNode(GrammarParseNode):
  def buildParseGraph(self):
    optionNodes = []
    optionLines = self.line.split("|")
    for optionLine in optionLines:
      optionNodes.append(SequentialParseNode(optionLine))
    return optionNodes

  def tryMatch(self, input, ruleDictionary):
    inputCopy = input
    for optionParseNode in self.parseGraph:
      (doesMatch, processedInput) = optionParseNode.tryMatch(input, ruleDictionary)

      if doesMatch:
        break

    return (doesMatch, processedInput if doesMatch else inputCopy)


class GrammarRule:
  def __init__(self, name, line):
    self.name = name
    self.line = line
    self.parseGraph = self.buildParseGraph()

  def buildParseGraph(self):
    return OptionParseNode(self.line)

  def tryMatch(self, input, ruleDictionary):
    return self.parseGraph.tryMatch(input, ruleDictionary)

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

count = 0
debugTestLineCounter = 1
for testLine in testLines:
  if DEBUG:
    print(f"line to test: {testLine}")

  (doesMatch, processedInput) = grammarDictionary["0"].tryMatch(testLine, grammarDictionary)
  # if it matches and all input was processed we have a hit
  if doesMatch and len(processedInput) == 0:
    print(f"matched line {testLine}")
    count += 1
  
  if DEBUG:
    print("==================")

  if DEBUG and debugTestLineCounter == DEBUG_TEST_LINE_COUNT:
    break
  debugTestLineCounter += 1

print(count)
