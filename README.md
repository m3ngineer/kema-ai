# KEMA Texting Buddy
KEep Me Accountable is a SMS/text-based bot that interacts with you in a way that helps you achieve your personal and professional goals.

We all have todo lists. And sometimes certain items tend to drop off the list without being completed, or keeping staying on it. KEMA acts as an accountability buddy that helps you overcome blocking emotions and keeps you living your best life!

# The Framework:
1. Start with a vision. Think about what the future could be. Alternatively, what's the anti-future?
1. Identify why you might not have accomplished this vision already. What's been holding you back?
1. Break down that vision into actionable pieces. What's something every week that you can do in order to achieve that vision? Think small and practically. Who do you have to be to overcome the barrier you identified?
1. Set a deadline. When will you accomplish this vision be?
1. Create a schedule. Take those actionable fragments and apply them to a calendar. If you did these actions consistently until the deadline, would you feel satisfied that you have achieved your vision?

## Sample conversation
- What task would you like to complete this week?
- When would you like to do it by?
- I'll send you a reminder 1 day in advanced
- Have you completed your task yet?
- What are you feeling when you think about this task?
- What impact does that emotion have on you? Does it affect other parts of your life?
- Who do you become when you do this task?
- Would you like to schedule a new task?
- Repeat

## Backend deets
- Text number from Twilio
- Process text content and send response
- Save response in conversation database
- Save goals/reminders in reminder database
- Check database every 4 hours; send reminders and alerts based on reminder database

## Architecture

![KEMA architecture diagram](/img/kema_architecture.png)
