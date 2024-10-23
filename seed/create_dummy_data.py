# Import necessary models
from main_application.models import Source, FollowUp, Message, Chat

# Create Source instances
source1 = Source.objects.create(text="FAR for R5 parcel", favicon="https://example.com/favicon1.ico", title="source")
source2 = Source.objects.create(text="Structural requirement for a 3 story home", favicon="https://example.com/favicon2.ico", title="source")
# Add more sources as needed

# Create FollowUp instances
follow_up1 = FollowUp.objects.create(question="Explore zoning regulations and constraints for 123 Main Street to align your development with local guidelines.", answer="Explore zoning regulations and constraints for 123 Main Street to align your development with local guidelines.")
follow_up2 = FollowUp.objects.create(question="Another follow-up question?", answer="Another follow-up answer.")
# Add more follow-ups as needed

# Create Message instance
message = Message.objects.create(user_chat="User's chat message", bot_chat_answer="Bot's chat answer")

# Create Chat instance
chat = Chat.objects.create(message=message, bot_chat_answer="Bot's chat answer", sources=[source1, source2], follow_up=[follow_up1, follow_up2])

# Print created objects
print("Source instances:", Source.objects.all())
print("FollowUp instances:", FollowUp.objects.all())
print("Message instance:", Message.objects.all())
print("Chat instance:", Chat.objects.all())
