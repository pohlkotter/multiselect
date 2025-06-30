A graphical simulation of cultural evolution. Inspired by https://bookdown.org/amesoudi/ABMtutorial_bookdown/model11.html and https://peterturchin.com/book/ultrasociety/

Prompt:
I want to write an object-oriented, graphical simulation in python that demonstrates multi-level selection the rules are as follows:

1\. Every individual is represented by a object that (in the first version) has three attributes  
  1.1 "role": An enum attribute marking the individual either as a cooperator (C), a punisher (P)  or a defector (D, may be also called freerider)    
  1.2 "payoff" a floating point value between 0 and 1 (=100%). All individuals start with a baseline payoff of 1, from which various costs are subtracted in the different stages.    
  1.3 "cooperates" a boolean value that indicates, whether the individual cooperates or not, may be left unintialized as it is set in the first stage (see 3.1.1 below).  


2\. groups can be lists of individuals (1st order groups) or lists of groups (higher order groups). For simulation purposes all groups on a specific level have the same size.

3\. for each (first or higher order) group, there are several transformation methods representing the stages that each simulation turn is comprised of  
  3.1 Stage 1 "Cooperation": an internal transformation (no arguments) for each individual of the group, no return value, but "cooperates" and "payoff" are modified:  
    3.1.1 The "cooperates" values are calculated as follows: C and P cooperate at a rate of 100% - e (with e being a constant refleting an error), whereas D never cooperate.     
    3.1.2 "payoff" changes due to cooperation costs and gains:  
      3.1.2.1 Each cooperating individual reduces its payoff value by a constant value (initially defined as 0.2 or 20%) reflecting the cost of cooperation.    
      3.1.2.2 Every individual increases its payoff by the half of the percentage of cooperating individuals in its first order group (payoff is of course capped at 1=100%)  

  3.2 Stage 2 "Punishment": an internal transformation (no arguments) of the group's individuals. Note that it deals within the first order groups (so for higher order groups, the following mechanism iterates over their first level groups)  
    3.2.1 For each first level group, its Punishers (Ps) punish every individual in their group who defected in the first stage.  
    3.2.2 Punishment reduces each punished individual payoff by p/n at a cost of k/n to the punisher, where n is the number of non-cooperators determined in stage 1 (see 3.1.1).  
    3.2.3 We set p=0.8 and k=0.2  
    3.2.4 The method does not return anything, but the group's state (payoffs of individuals) is altered

  3.3 Stage 3 "payoff-biased learning": an internal transformation of the group's individuals. This happens either within the first order groups or between first order groups. Therefore it should be only defined for second order or higher groups. For each individual i the following is performed  
    3.3.1 With probability 1−m, i interacts with a random member of their own first order group.  
    3.3.2 With probability m, i interacts with a random member of another first order group within that second order group.  
    3.3.3 We will set m=0.01, giving a 1/100 chance of interacting with members of other groups.  
    3.3.4 Once the random member c has been chosen, i may take over the role of c based on the payoffs p_c of c and p_i with the chance of p_c / (p_c  +  p_i)  
    3.3.5 The method does not return anything, but the group's state (payoffs of individuals) is altered

  3.4 Stage 4 "competition": for each nth order group the (n-1)th order subgroups compete each with one (randomly selected) other at a certain chance (competitionChance = 0.1) as follows:  
    3.4.1 For group g1 and g2, the chance that g1 wins over g2 is 0.5 + (c1 - c2)/2 with c1 being the relative number of cooperators and punishers of g1 and c2 the same for g2  
    3.4.2 Groups that lose a contest are replaced with a replica of the winning group, i.e. one that contains the same set of attributes on individual level as the winning group  

  3.5 Stage 5 "mutation": There is a small chance (mutationChance = 0.05) for each individuum that it changes its role, keeping all other attributes

4\. The graphical representation is as follows  
  4.1 Individuals are small squares with colors: green for cooperators, black for punishers and red for defectors  
  4.2 The square is filled from the bottom with the amount of payoff: 0 resulting in an empty frame square, 0.5 half filled, 1 completely filled square  
  4.3 The "cooperates" field is represented by a small check mark attached to the individual if "true" and a missing check mark if "false"  
  4.3 The groups are marked as rectangular frames that envelop all individual squares or subgroup frames  
  4.4 The stages run with a speed that can be set via an input field or ruler  
  4.5 The individual stages shows for each selected group or individual a black frame and a briefly displayed dotted line for the individuals or groups interacting:  
    4.5.1 In Stage 2 it connects the punisher and the defectors in the group while punishing is done  
    4.5.2 In Stage 3 it connects i with c while learning is done  
    4.5.3 In Stage 4 it connects the two subgroups that compeate wich each other

5\. The code shall be organized in small maintainable files with constants all in a separate file