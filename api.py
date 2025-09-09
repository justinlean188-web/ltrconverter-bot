import re
import json
from collections import OrderedDict
from flask import Flask, request, jsonify
import requests # Make sure to run: pip install requests
from datetime import datetime, timedelta
from telegram.ext import CommandHandler
from telegram.ext import Application, ContextTypes
import uuid
import time
from functools import wraps



# ==============================================================================
#  PARSING LOGIC
# ==============================================================================
BOT_TOKEN = "8083952920:AAFQD3RGAW_OdM2pZscy5NeReqUq-GytXrI"
# nich
# CHAT_ID = -1002886297196 
# bot2
CHAT_ID = -4938742244 
# testing
# CHAT_ID = -1002793925276
# Define the times for each lottery
KH_TIMES = ["8:45AM", "10:35AM", "1:00PM", "3:45PM", "6:00PM", "7:45PM"]
VN_TIMES = ["10:41AM", "1:30PM", "4:30PM", "6:30PM", "7:36PM"]
USA_TIMES = ["8:00AM", "10:00AM", "12:00PM", "2:00PM", "4:00PM", "6:00PM"]

def parse_input(text: str) -> dict | None:
    # Added the new 'dal' parser to the list
    parsing_functions = [
      
        parse_num_op_equals_money,
        parse_num_dash_money_post,
        parse_multi_dot_numbers_money,
        parse_num_op_money,
        parse_special_x,
        parse_num_dash_money,
        parse_simple_number_no_money,
        parse_num_space_money,
        parse_num_column_money,
        parse_num_dal_num_equals_money,
        parse_num_op_num_equals_money, 
        parse_num_dot_money,
        parse_num_slash_money,
        parse_num_money_kun,
        parse_num_symbol_op_money,
        parse_multi_ou_numbers_money,
        parse_num_op_symbol_money,
        parse_multi_bet_line,
        parse_multi_x_kun_money_riel
        
    ]
    for func in parsing_functions:
        result = func(text)
        if result:
            return result
    return None 

def normalize_input(parsed_bet):
    """
    Normalize OCR errors in parsed bet dict.
    Replace 'O'/'o' with '0' only in Number and Money fields.
    """
    for key in ["Number", "Number1", "Number2", "Money"]:
        if key in parsed_bet and isinstance(parsed_bet[key], str):
            parsed_bet[key] = parsed_bet[key].replace("O", "0").replace("o", "0")
    return parsed_bet


def parse_num_money_kun(text):
    pattern = re.compile(
    r"^(?P<post>\S+)\s+"
    r"(?P<number>\d{2,3})\s*"
    r"(?:[=:-]\s*)?"
    r"(?P<money>\d{1,6})គុណ$"
)
    match = pattern.match(text)
    if match:
        d = match.groupdict()
        result = OrderedDict([("Number", d["number"]),("Operator", "x"),  ("Post", d["post"])])
        if d["money"]:
            result["Money"] = d["money"]
        return result
    return None

pattern = re.compile(
    r"^(?P<number>\d{2,3})(?:-|\.{1,2})(?P<money>\d{3,6})\.(?P<post>\w+)$"
)

tests = ["123.3000.ABCD", "123..3000.ABCD", "15-1000.ABCD"]

for test in tests:
    match = pattern.match(test)
    print(test, "->", match.groupdict() if match else "No match")
    
def parse_num_dash_money_post(text):
    pattern = re.compile(
        r"^(?P<number>\d{2,3})(?:-|\.{1,2})(?P<money>\d{3,6})\.(?P<post>\w+)$"
    )
    match = pattern.match(text)
    
    if match:
        d = match.groupdict()
        result = OrderedDict([("Number", d["number"]), ("Post", d["post"])])
        if d["money"]:
            result["Money"] = d["money"].replace('r', '')
        return result
    return None

def parse_simple_number_no_money(text):
    """
    Parses a line with just a post and a number.
    Example: ABCD 45
    """
    pattern = re.compile(r"^(?P<post>\w+)\s+(?P<number>\d{2,3})$")
    match = pattern.match(text)
    if match:
        d = match.groupdict()
        result = OrderedDict([("Number", d["number"]), ("Post", d["post"])])
        return result
    return None


def parse_num_space_money(text):
    pattern = re.compile(r"^(?P<post>\w+)\s+(?P<number>\d{2,3})\s+(?P<money>\d{0,6})r?$")
    match = pattern.match(text)
    if match:
        d = match.groupdict()
        result = OrderedDict([("Number", d["number"]), ("Post", d["post"])])
        if d["money"]:
            result["Money"] = d["money"].replace('r', '')
        return result
    return None

def parse_num_dal_num_equals_money(text):
    pattern = re.compile(
    r"^(?P<post>\S+)\s+"
    r"(?P<num1>\d{2,3})ដល(?P<num2>\d{2,3})\s*"
    r"(?:[=:]\s*)?"
    r"(?P<money>\d{1,6})r?$"
)
    match = pattern.match(text)
    if match:
        d = match.groupdict()
        result = OrderedDict([
            ("Number1", d["num1"]),
            ("Operator", "-"),
            ("Number2", d["num2"]),
            ("Post", d["post"])
        ])
        if d["money"]:
            result["Money"] = d["money"].replace('r', '')
        return result
    return None

def parse_num_op_num_equals_money(text):
    pattern = re.compile(
    r"^(?P<post>\w+)\s+"
    r"(?P<num1>\d{2,3})\s*"
    r"(?P<op>[-)><(_,])\s*"
    r"(?P<num2>\d{2,3})\s*"
    r"(?:[=:),.]\s*)?"      # optional = or :
    r"(?P<money>\d{1,6})r?$"
)
    match = pattern.match(text)
    if match:
        d = match.groupdict()
        operator = "-" if d["op"] == ")" else d["op"]
        result = OrderedDict([
            ("Number1", d["num1"]),
            ("Operator", operator),
            ("Number2", d["num2"]),
            ("Post", d["post"])
        ])
        if d["money"]:
            result["Money"] = d["money"].replace('r', '')
        return result
    return None
def parse_num_op_equals_money(text):
    """
    Parses patterns like:
    - A 30x=100
    - B 45*=500
    """
    pattern = re.compile(
        r"^(?P<post>\w+)\s+"
        r"(?P<number>\d{2,3})\s*"
        r"(?P<op>[Xx×*])\s*"      # Multiplication operators
        r"(?:[=:])\s*"           # Equals or Colon separator
        r"(?P<money>\d{1,6})r?$"
    )
    match = pattern.match(text)
    if match:
        d = match.groupdict()
        result = OrderedDict([
            ("Number", d["number"]),
            ("Operator", "x"), # Normalize operator to 'x'
            ("Post", d["post"]),
            ("Money", d["money"].replace('r', ''))
        ])
        return result
    return None
def parse_num_op_money(text):
    pattern = re.compile(r"^(?P<post>\w+)\s+(?P<num>\d{2,3})\s*(?P<op>[Xx×+_*\>\):=\.])\s*(?P<money>\d{0,6})r?$", re.UNICODE)
    match = pattern.match(text)
    if match:
        d = match.groupdict()
        output = OrderedDict([("Number", d["num"]), ("Post", d["post"])])
        if d["op"] in ['x', '>']:
            output["Operator"] = d["op"]
        elif d["op"] == '*':
            output["Operator"] = 'x'
        elif d["op"] == '×':
            output["Operator"] = 'x'
        elif d["op"] == 'X':
            output["Operator"] = 'x'
        elif d["op"] == '+':
            output["Operator"] = 'x'
        elif d["op"] == ')':
            output["Operator"] = '>'
        if d["money"]:
            output["Money"] = d["money"].replace('r', '')
        return output
    return None
def parse_num_symbol_op_money(text):
    pattern = re.compile(
    r"^(?P<post>\w+)\s+"
    r"(?P<num>\d{2,3})\s*"
    r"[:;,-]\s*"  # allow : or ;
    r"(?P<op>[Xx×+_*\>\):=\.])\s*"
    r"(?P<money>\d{0,6})r?$",
    re.UNICODE
)
    match = pattern.match(text)
    if match:
        d = match.groupdict()
        output = OrderedDict([("Number", d["num"]), ("Post", d["post"])])
        if d["op"] in ['x', '>']:
            output["Operator"] = d["op"]
        elif d["op"] == '*':
            output["Operator"] = 'x'
        elif d["op"] == '×':
            output["Operator"] = 'x'
        elif d["op"] == 'X':
            output["Operator"] = 'x'
        elif d["op"] == '+':
            output["Operator"] = 'x'
        elif d["op"] == ')':
            output["Operator"] = '>'
        if d["money"]:
            output["Money"] = d["money"].replace('r', '')
        return output
    return None

def parse_num_op_symbol_money(text):
    pattern = re.compile(
    r"^(?P<post>\w+)\s+"
    r"(?P<num>\d{2,3})\s*"
    r"(?P<op>[Xx×+_*\>\):=\.])\s*"
    r"[:;,-=]\s*"  # allow : or ;
    r"(?P<money>\d{0,6})r?$",
    re.UNICODE
)
    match = pattern.match(text)
    if match:
        d = match.groupdict()
        output = OrderedDict([("Number", d["num"]), ("Post", d["post"])])
        if d["op"] in ['x', '>']:
            output["Operator"] = d["op"]
        elif d["op"] == '*':
            output["Operator"] = 'x'
        elif d["op"] == '×':
            output["Operator"] = 'x'
        elif d["op"] == 'X':
            output["Operator"] = 'x'
        elif d["op"] == '+':
            output["Operator"] = 'x'
        elif d["op"] == ')':
            output["Operator"] = '>'
        if d["money"]:
            output["Money"] = d["money"].replace('r', '')
        return output
    return None
def parse_special_x(text):
    pattern = re.compile(r"^(?P<post>\w+)\s+(?P<num1>\d{2,3})\s*-\s*(?P<num2>\d{2,3})\s*[x×]\s*(?P<money>\d{0,6})r?$")
    match = pattern.match(text)
    if match:
        d = match.groupdict()
        result = OrderedDict([
            ("Number1", d["num1"]),
            ("Operator1", "-"),
            ("Number2", d["num2"]),
            ("Operator2", "x"),
            ("Post", d["post"])
        ])
        if d["money"]:
            result["Money"] = d["money"].replace('r', '')
        return result
    return None

def parse_num_dash_money(text):
    pattern = re.compile(r"^(?P<post>\w+)\s+(?P<number>\d{2,3})\s*-\s*(?P<money>\d{0,6})r?$")
    match = pattern.match(text)
    if match:
        d = match.groupdict()
        result = OrderedDict([("Number", d["number"]), ("Post", d["post"])])
        if d["money"]:
            result["Money"] = d["money"].replace('r', '')
        return result
    return None
def parse_num_column_money(text):
    pattern = re.compile(r"^(?P<post>\w+)\s+(?P<number>\d{2,3})\s*\,\s*(?P<money>\d{0,6})r?$")
    match = pattern.match(text)
    if match:
        d = match.groupdict()
        result = OrderedDict([("Number", d["number"]), ("Post", d["post"])])
        if d["money"]:
            result["Money"] = d["money"].replace('r', '')
        return result
    return None

def parse_num_dot_money(text):
    pattern = re.compile(
    r"^(?P<post>\w+)\s+(?P<number>\d{2,3})\s*\.\.?[\s]*(?P<money>\d{0,6})r?$"
    )

    match = pattern.match(text)
    if match:
        d = match.groupdict()
        result = OrderedDict([("Number", d["number"]), ("Post", d["post"])])
        if d["money"]:
            result["Money"] = d["money"].replace('r', '')
        return result
    return None

def parse_num_slash_money(text):
    pattern = re.compile(r"^(?P<post>\w+)\s+(?P<number>\d{2,3})\s*/\s*(?P<money>\d{0,6})r?$")
    match = pattern.match(text)
    if match:
        d = match.groupdict()
        result = OrderedDict([("Number", d["number"]), ("Post", d["post"])])
        if d["money"]:
            result["Money"] = d["money"].replace('r', '')
        return result
    return None

def parse_multi_dot_numbers_money(text):
    """
    Matches: POST 30.32.34.10000
    Returns: [{'Number': '30', 'Post': POST, 'Money': '10000'}, ...]
    """
    pattern = re.compile(r"^(?P<post>\w+)\s+((\d{2,3}\.)+)(?P<money>\d{0,6})r?$")
    match = pattern.match(text)
    if match:
        d = match.groupdict()
        numbers_part = text.split()[1]
        *numbers, money = numbers_part.split('.')
        results = []
        for num in numbers:
            results.append(OrderedDict([
                ("Number", num),
                ("Post", d["post"]),
                ("Money", money.replace('r', ''))
            ]))
        return results  # Return a list of bets
    return None

def parse_multi_ou_numbers_money(text):
    """
    Matches: POST 30>32>34>10000 or POST 30)32)34)10000
    Returns: [{'Number': '30', 'Post': POST, 'Money': '10000'}, ...]
    """
    pattern = re.compile(r"^(?P<post>\w+)\s+(?P<numbers>(?:\d+[)>])+)(?P<money>\d{0,6})r?$")   
    match = pattern.match(text)
    if match:
        d = match.groupdict()
        numbers = re.split(r"[)>]", d["numbers"])
        results = []
        for num in numbers[:-1]:
            results.append(OrderedDict([
                ("Number", num),
                ("Operator", ">"),
                ("Post", d["post"]),
                ("Money", d["money"])
            ]))
        return results
    return None

def parse_multi_x_kun_money_riel(text):
    """
    Handles multiple numbers separated by 'x' and extracts money.
    Example: ABCD 10x20x30x1000 or ABCD 10*20x30X1000
    Returns: [{'Number': '10', 'Operator': 'x', 'Post': 'ABCD', 'Money': '1000'}, ...]
    """
    pattern = re.compile(r"^(?P<post>\w+)\s+(?P<numbers>(?:\d+[xX*×])+)(?P<money>\d+)៛?$")
    match = pattern.match(text)
    
    if match:
        d = match.groupdict()
        numbers = re.split(r"[xX*×]", d["numbers"])
        results = []
        for num in numbers[:-1]:
            results.append(OrderedDict([
                ("Number", num),
                ("Operator", "x"),
                ("Post", d["post"]),
                ("Money", d["money"])
            ]))
        return results
    return None


def parse_multi_bet_line(text):
    """
    NEW: Handles a line with a post followed by multiple, space-separated bets.
    Example: ABCD 10-200 30-1000 100x200
    """
    parts = text.strip().split()
    if len(parts) < 2:
        return None

    post = parts[0]
    bet_parts = parts[1:]
    results = []

    for bet_str in bet_parts:
        # Try to match the 'number-money' format
        match_dash = re.match(r"^(?P<number>\d+)-(?P<money>\d+)$", bet_str)
        if match_dash:
            d = match_dash.groupdict()
            results.append(OrderedDict([
                ("Number", d["number"]),
                ("Post", post),
                ("Money", d["money"])
            ]))
            continue # Move to the next bet part

        # If that fails, try to match the 'numberxmoney' format
        match_x = re.match(r"^(?P<number>\d+)x(?P<money>\d+)$", bet_str)
        if match_x:
            d = match_x.groupdict()
            results.append(OrderedDict([
                ("Number", d["number"]),
                ("Operator", "x"),
                ("Post", post),
                ("Money", d["money"])
            ]))
    
    # Only return a result if we successfully parsed at least one bet
    return results if results else None
def get_next_time(time_type="vn"):
    now = datetime.now()
    if time_type.lower() == "kh":
        time_list = KH_TIMES
    elif time_type.lower() == "usa":
        time_list = USA_TIMES
    else:
        time_list = VN_TIMES

    today_times = []
    for t in time_list:
        t_obj = datetime.strptime(t, "%I:%M%p")
        today_time = now.replace(hour=t_obj.hour, minute=t_obj.minute, second=0, microsecond=0)
        today_times.append(today_time)

    for t, t_str in zip(today_times, time_list):
        if t > now:
            ampm = t.strftime("%p")
            return t_str, ampm
    # If none found, return the first time of the next day
    ampm = today_times[0].strftime("%p")
    return time_list[0], ampm

def map_post_code(code: str, command_time: str) -> str:
    """
    Map numeric post codes based on the game time.
    """
    if command_time in ["6:30", "7:30"]:
        if code == "5" or code == "+5" or code == "5p" or code == "5+" or code == "5P":
            return "ABCD"
        elif code == "6" or code == "+6" or code == "6p" or code == "6+":
            return "ABCD"
        elif code == "7" or code == "+7" or code == "7p" or code == "7+":
            return "ABCD"
    else:
        if code == "5" or code == "+5" or code == "5p" or code == "5+":
            return "ABCDF"
        elif code == "6" or code == "+6" or code == "6p" or code == "6+":
            return "ABCDFIN"
        elif code == "7" or code == "+7" or code == "7p" or code == "7+":
            return "ABCDFIN"
    return code.upper()


# ==============================================================================
#  API UTILITY FUNCTIONS
# ==============================================================================

def api_response(success=True, message="", data=None, status_code=200):
    """
    Standardized API response format for Java consumption
    """
    response = {
        "success": success,
        "message": message,
        "timestamp": time.time(),
        "data": data if data is not None else {}
    }
    return jsonify(response), status_code

def validate_json_request(f):
    """
    Decorator to validate JSON requests
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return api_response(False, "Request must be JSON", status_code=400)
        return f(*args, **kwargs)
    return decorated_function

def handle_api_errors(f):
    """
    Decorator to handle common API errors
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return api_response(False, f"Invalid data: {str(e)}", status_code=400)
        except KeyError as e:
            return api_response(False, f"Missing required field: {str(e)}", status_code=400)
        except Exception as e:
            return api_response(False, f"Internal server error: {str(e)}", status_code=500)
    return decorated_function

# ==============================================================================
#  FLASK WEB SERVER
# ==============================================================================
app = Flask(__name__)
# Enhanced command queue with ID tracking and timestamps
command_queue = {}  # Dictionary: {command_id: {"command": data, "timestamp": time, "status": "pending"}}
INCOMPLETE_BETS_LIST = []

def add_command_to_queue(command_data):
    """Helper function to add a command to the queue with unique ID and timestamp"""
    global command_queue
    command_id = str(uuid.uuid4())
    command_queue[command_id] = {
        "command": command_data,
        "timestamp": time.time(),
        "status": "pending"
    }
    return command_id 
@app.route("/get_command", methods=['GET'])
@handle_api_errors
def get_red_command():
    """
    Enhanced endpoint for Java to retrieve pending commands
    Returns standardized JSON response with command metadata
    """
    global command_queue
    
    pending_commands = {}
    total_pending = 0
    
    for cmd_id, cmd_data in command_queue.items():
        if cmd_data["status"] == "pending":
            pending_commands[cmd_id] = {
                "command": cmd_data["command"],
                "timestamp": cmd_data["timestamp"],
                "age_seconds": time.time() - cmd_data["timestamp"]
            }
            total_pending += 1
    
    return api_response(
        success=True,
        message=f"Found {total_pending} pending commands",
        data={
            "commands": pending_commands,
            "total_pending": total_pending,
            "queue_size": len(command_queue)
        }
    )

@app.route("/clear_command", methods=['POST'])
@validate_json_request
@handle_api_errors
def clear_command():
    """
    Enhanced command clearing endpoint for Java
    POST body: {"command_ids": ["id1", "id2"]} or {"clear_all": true}
    """
    global command_queue
    
    data = request.json
    
    if data.get("clear_all"):
        # Clear all commands
        cleared_count = len(command_queue)
        command_queue.clear()
        return api_response(
            success=True,
            message="All commands cleared successfully",
            data={
                "cleared_count": cleared_count,
                "operation": "clear_all"
            }
        )
    
    command_ids = data.get("command_ids", [])
    if not command_ids:
        return api_response(
            success=False,
            message="No command_ids provided",
            status_code=400
        )
    
    cleared_count = 0
    not_found_ids = []
    
    for cmd_id in command_ids:
        if cmd_id in command_queue:
            del command_queue[cmd_id]
            cleared_count += 1
        else:
            not_found_ids.append(cmd_id)
    
    return api_response(
        success=True,
        message=f"Cleared {cleared_count} commands",
        data={
            "cleared_count": cleared_count,
            "requested_count": len(command_ids),
            "not_found_ids": not_found_ids,
            "operation": "selective_clear"
        }
    )

@app.route("/queue_status", methods=['GET'])
@handle_api_errors
def queue_status():
    """Enhanced queue status endpoint for Java monitoring"""
    global command_queue
    
    pending_count = sum(1 for cmd in command_queue.values() if cmd["status"] == "pending")
    completed_count = sum(1 for cmd in command_queue.values() if cmd["status"] == "completed")
    
    queue_details = {}
    oldest_command = None
    newest_command = None
    
    current_time = time.time()
    
    for cmd_id, cmd_data in command_queue.items():
        age_seconds = current_time - cmd_data["timestamp"]
        
        queue_details[cmd_id] = {
            "status": cmd_data["status"],
            "timestamp": cmd_data["timestamp"],
            "command_type": cmd_data["command"].get("type", "betting"),
            "age_seconds": age_seconds,
            "age_minutes": round(age_seconds / 60, 2)
        }
        
        # Track oldest and newest commands
        if oldest_command is None or cmd_data["timestamp"] < oldest_command:
            oldest_command = cmd_data["timestamp"]
        if newest_command is None or cmd_data["timestamp"] > newest_command:
            newest_command = cmd_data["timestamp"]
    
    return api_response(
        success=True,
        message="Queue status retrieved successfully",
        data={
            "summary": {
                "total_commands": len(command_queue),
                "pending_commands": pending_count,
                "completed_commands": completed_count,
                "oldest_command_age": round(current_time - oldest_command, 2) if oldest_command else 0,
                "newest_command_age": round(current_time - newest_command, 2) if newest_command else 0
            },
            "queue_details": queue_details
        }
    )

@app.route("/send_command", methods=['POST'])
@validate_json_request
@handle_api_errors
def send_command():
    """Enhanced command submission endpoint with better validation and responses"""
    global command_queue
    
    data = request.json
    if "text" not in data:
        return api_response(
            success=False,
            message="Missing required field: text",
            status_code=400
        )
    
    raw_text = request.json['text']
    text = normalize_input(raw_text)
    print("Received text:", text)

    # --- FIX: Initialize variables at the top to prevent UnboundLocalError ---
    time_types_to_process = []
    name_str = ""
    manual_time_str = "" # This prevents a potential error if 'vn_manual' is used

    if "យួន" in text:
        time_types_to_process.append('vn')
    if "ខ្មែរ" in text:
        time_types_to_process.append('kh')
    if "អន្តរជាតិ" in text:
        time_types_to_process.append('usa')
    if "ជាតិ" in text:
        time_types_to_process.append('usa')
    lines = text.strip().split('\n')
    first_line_parts = lines[0].strip().split()
    print("First line parts:", first_line_parts)
    # --- Handle Resend Photo command ---
    if first_line_parts[0].upper() == "SEND":
        command_id = add_command_to_queue({"type": "resend"})
        print(f"Queued resend command with ID: {command_id}")
        return "ok"
    
    # --- Handle Setup Bot command ---
    if first_line_parts[0].upper() == "SETUP_BOT":
        command_id = add_command_to_queue({"type": "setup_bot"})
        print(f"Queued setup_bot command with ID: {command_id}")
        return "ok"
    
    # --- Handle CONFIRM command (no changes here) ---
    #how it works:
    #1. user send /cf 1 nich 10:30
    #2. bot will parse the command and send the command to the API
    #3. API will send the command to the Android app
    #4. Android app will confirm the invoice and send the confirmation message to the Telegram bot
    #5. Telegram bot will send the confirmation message to the user 
    if first_line_parts[0].upper() == "CONFIRM" and len(first_line_parts) >= 4:
        invoice_id = first_line_parts[1]
        invoice_name = first_line_parts[2]
        invoice_time_raw = first_line_parts[3].strip()
        time_type = None
        print("Parsed id:", invoice_id, "Parsed name:", invoice_name, "Parsed time:", invoice_time_raw, "Parsed time type:", time_type)
        # Check if the input is a time type indicator (vn, kh, usa)
        if invoice_time_raw.lower() == 'vn':
            time_type = 'vn'
            # Get the next VN time
            next_time, _ = get_next_time('vn')
            invoice_time = next_time.replace("AM", "").replace("PM", "").strip()
        elif invoice_time_raw.lower() == 'kh':
            time_type = 'kh'
            # Get the next KH time
            next_time, _ = get_next_time('kh')
            invoice_time = next_time.replace("AM", "").replace("PM", "").strip()
        elif invoice_time_raw.lower() == 'usa':
            time_type = 'usa'
            # Get the next USA time
            next_time, _ = get_next_time('usa')
            # replace :00 with empty
            invoice_time = next_time.replace("AM", "").replace("PM", "").replace(":00", "").strip()
        # USA: user inputs 'usa' or 'usa8', etc.
        elif invoice_time_raw.lower().startswith('usa'):
            time_type = 'usa'
            hour_part = invoice_time_raw[3:]
            if hour_part.isdigit():
                invoice_time = f"{int(hour_part)}:00"
            else:
                from datetime import datetime
                now = datetime.now()
                from_date = lambda t: datetime.strptime(t, "%I:%M%p")
                min_diff = None
                closest_time = None
                for t in USA_TIMES:
                    t_obj = from_date(t)
                    t_today = now.replace(hour=t_obj.hour, minute=t_obj.minute, second=0, microsecond=0)
                    diff = (t_today - now).total_seconds()
                    if diff < 0:
                        diff += 24 * 3600
                    if min_diff is None or diff < min_diff:
                        min_diff = diff
                        closest_time = t
                invoice_time = closest_time.replace("AM", "").replace("PM", "").strip()
        else:
            # It's an actual time, so parse it normally
            invoice_time = invoice_time_raw.replace("AM", "").replace("PM", "").strip()
            def match_time(t, time_list):
                t_clean = t.replace("AM", "").replace("PM", "").strip()
                for entry in time_list:
                    if t_clean == entry.replace("AM", "").replace("PM", "").strip():
                        return True
                return False
            if match_time(invoice_time, VN_TIMES):
                time_type = 'vn'
            elif match_time(invoice_time, KH_TIMES):
                time_type = 'kh'
            elif match_time(invoice_time, USA_TIMES):
                time_type = 'usa'
            else:
                time_type = 'unknown'
        print("Parsed id:", invoice_id, "Parsed name:", invoice_name, "Parsed time:", invoice_time, "Parsed time type:", time_type)
        command_id = add_command_to_queue({"type": "confirm", "id": invoice_id, "name": invoice_name, "time": invoice_time, "time_type": time_type})
        print(f"Queued confirm command with ID: {command_id}")
        return "ok"

    # --- Determine fallback time types and name ---
    if not time_types_to_process:
        if len(first_line_parts) > 0 and first_line_parts[0].lower() == "usa":
            time_types_to_process.append("usa")
            name_str = first_line_parts[1] if len(first_line_parts) > 1 else ""
        elif len(first_line_parts) > 0 and first_line_parts[0].lower() in ("kh", "vn"):
            time_types_to_process.append(first_line_parts[0].lower())
            name_str = first_line_parts[1] if len(first_line_parts) > 1 else ""
        elif len(first_line_parts) > 0 and re.match(r"\d{1,2}:\d{2}", first_line_parts[0]):
            time_types_to_process.append("vn_manual") 
            manual_time_str = first_line_parts[0].replace("AM", "").replace("PM", "").strip()
            name_str = first_line_parts[1] if len(first_line_parts) > 1 else ""
        else:
            time_types_to_process.append("vn")
            name_str = first_line_parts[0] if len(first_line_parts) > 0 and not any(char.isdigit() for char in first_line_parts[0]) else ""
    else:
        # Keywords were found, so find the name among the other parts
        for part in first_line_parts:
            # A name should not be a keyword or contain only digits
            if part.lower() not in ["ខ្មែរ", "យួន","អន្តរជាតិ","ជាតិ" "kh", "vn", "usa", "fast"] and not re.match(r"\d{1,2}:\d{2}", part):
                name_str = part
                break

    if time_types_to_process[0] == "vn_manual":
        command_time = manual_time_str
    else:
        next_time, _ = get_next_time(time_types_to_process[0])
        command_time = next_time.replace("AM", "").replace("PM", "").strip()

    # --- Parsing logic (no changes here) ---
    multiplier = 1
    if any("x100" in part.lower() for part in first_line_parts):
        multiplier = 100

    post_lines = lines[1:]
    if post_lines and any(char.isdigit() for char in post_lines[0]):
        post_lines.insert(0, "ABCD")
    elif not post_lines and any(char.isdigit() for char in lines[0]):
        # This handles cases like "kun\n90-99=1000" where there's no post line
        post_lines = ["ABCD"] + lines[1:]
    elif not post_lines:
        post_lines = ["ABCD"]

    post_aliases = {
    "4": "ABCD",
    "4p": "ABCD",
    "4*": "ABCD",
    "*4": "ABCD",
    "4+": "ABCD",
    "4post": "ABCD",
    "+4": "ABCD",
    "lo": "L",
}

    global INCOMPLETE_BETS_LIST
    INCOMPLETE_BETS_LIST.clear() # Clear the list for every new message

    data_list = []
    current_post = None
    last_money = None 
    star_bets = []

    for line in post_lines:
        raw_line = line.strip()
        if not raw_line:
            continue

        alias = post_aliases.get(raw_line.lower())
        if alias:
            current_post = alias
            continue

        if not any(char.isdigit() for char in raw_line) and "ដល" not in raw_line:
            current_post = raw_line.upper().replace(' ', '')
            continue

        if current_post:
            bet_line = raw_line.replace("O", "0").replace("o", "0")
            mapped_post = map_post_code(current_post, command_time)
            full_line = f"{mapped_post} {bet_line}"
            parsed = parse_input(full_line)

            if parsed:
                bets_to_process = parsed if isinstance(parsed, list) else [parsed]

                for p in bets_to_process:
                    p = normalize_input(p)

                    # 1. If money is explicitly provided, use it and remember it.
                    if p.get("Money") and p["Money"].isdigit():
                        current_money = str(int(p["Money"]) * multiplier)
                        p["Money"] = current_money
                        last_money = current_money 
                    
                    # 2. If no money is provided...
                    else:
                        if last_money:
                            # Use the last remembered amount.
                            p["Money"] = last_money
                        else:
                            # NO last money yet. This is an incomplete bet.
                            # Format it and add it to the global list.
                            bet_str = ""
                            if "Number1" in p: # For range bets like 90-99
                                bet_str = f"{p['Number1']}{p.get('Operator', '')}{p.get('Number2', '')}"
                            else: # For single number bets
                                bet_str = f"{p['Number']}{p.get('Operator', '')}"
                            INCOMPLETE_BETS_LIST.append(bet_str)
                    
                    if p.get("Star"):
                        star_bets.append(p)
                    data_list.append(p)

    # --- Grouping logic (no changes here) ---
    data_by_post = OrderedDict()
    for item in data_list:
        post_key = item['Post']
        if post_key not in data_by_post:
            data_by_post[post_key] = []
        data_by_post[post_key].append(item)

    # NEW: Re-order the posts to ensure 'L' is always last
    sorted_posts = OrderedDict()
    # First, add all posts that are NOT 'L'
    for post, bets in data_by_post.items():
        if post.upper() != 'L':
            sorted_posts[post] = bets
    # After all other posts, add the 'L' post if it exists
    if 'L' in data_by_post:
        sorted_posts['L'] = data_by_post['L']
    
    # Now, build the final structure using the re-ordered posts
    final_grouped_data = OrderedDict()
    for post, bets in sorted_posts.items(): # Use the newly sorted_posts
        if not bets: continue
        final_grouped_data[post] = []
        current_money_group = None
        for bet in bets:
            bet.pop("Post", None)
            money_val = bet.pop("Money", None)
            if current_money_group is None or current_money_group['money'] != money_val:
                new_group = OrderedDict([('money', money_val), ('bets', [bet])])
                final_grouped_data[post].append(new_group)
                current_money_group = new_group
            else:
                current_money_group['bets'].append(bet)
    
    # --- Loop and create commands ---
    if final_grouped_data:
        for time_type in time_types_to_process:
            # FIX: Initialize time_str here to ensure it's always set for the loop iteration
            time_str = ""

            if time_type == "vn_manual":
                time_str = manual_time_str
            else:
                next_time, _ = get_next_time(time_type)
                time_str = next_time.replace("AM", "").replace("PM", "").strip()
                if time_type == 'usa' and time_str.endswith(":00"):
                    time_str = time_str[:-3]

            final_command = {   
                "name": name_str,
                "time": time_str,
                "data": final_grouped_data
            }
            command_id = add_command_to_queue(final_command)
            print(f"Queued command for {time_type.upper()} at {time_str} with ID: {command_id}")



    # Return success response with command processing details
    return api_response(
        success=True,
        message="Command processed successfully",
        data={
            "processed_text": text,
            "commands_created": len(time_types_to_process),
            "time_types": time_types_to_process,
            "incomplete_bets": len(INCOMPLETE_BETS_LIST),
            "incomplete_bet_numbers": INCOMPLETE_BETS_LIST if INCOMPLETE_BETS_LIST else []
        }
    )

@app.route("/task_complete", methods=['GET', 'POST'])
@handle_api_errors
def task_complete():
    """
    Enhanced task completion endpoint for Java
    Sends final confirmation to Telegram and returns detailed status
    """
    global INCOMPLETE_BETS_LIST
    
    # Start with the standard success message
    message_text = "✅កត់រួចហើយ" 
    incomplete_bets_detected = bool(INCOMPLETE_BETS_LIST)
    
    # If the list is not empty, there were incomplete bets.
    if INCOMPLETE_BETS_LIST:
        # Join the problem numbers into a readable string
        problem_numbers_str = ", ".join(INCOMPLETE_BETS_LIST)
        
        # Create a detailed, multi-line warning message
        warning_text = (
            f"‼️ ការភ្នាល់ខ្លះមិនមានទឹកប្រាក់ទេ។\n"
            f"សូមពិនិត្យលេខ: **{problem_numbers_str}**"
        )
        message_text = f"{message_text}\n\n{warning_text}"
        
        # Store incomplete bets for response before clearing
        incomplete_bet_list = INCOMPLETE_BETS_LIST.copy()
        INCOMPLETE_BETS_LIST.clear()
    else:
        incomplete_bet_list = []

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message_text,
        "parse_mode": "Markdown"
    }
    
    telegram_success = False
    telegram_error = None
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            telegram_success = True
            print("Sent completion notification to Telegram.")
        else:
            telegram_error = f"Telegram API returned status {response.status_code}"
    except Exception as e:
        telegram_error = str(e)
        print(f"Failed to send Telegram notification: {e}")
    
    return api_response(
        success=True,
        message="Task completion processed",
        data={
            "telegram_notification_sent": telegram_success,
            "telegram_error": telegram_error,
            "incomplete_bets_detected": incomplete_bets_detected,
            "incomplete_bets": incomplete_bet_list,
            "completion_timestamp": time.time()
        }
    )
@app.route("/confirm_invoice", methods=['POST'])
@validate_json_request
@handle_api_errors
def confirm_invoice_api():
    """Enhanced invoice confirmation endpoint for Java integration"""
    data = request.json
    
    invoice_id = data.get("id")
    invoice_time = data.get("time")
    
    if not invoice_id or not invoice_time:
        return api_response(
            success=False,
            message="Missing required fields: id and time",
            status_code=400
        )
    
    # Validate invoice_id format
    try:
        int(invoice_id)  # Ensure it's numeric
    except ValueError:
        return api_response(
            success=False,
            message="Invalid invoice_id format - must be numeric",
            status_code=400
        )
    
    # Return confirmation data compatible with Android
    return api_response(
        success=True,
        message="Invoice confirmation processed",
        data={
            "confirmation": [{"id": invoice_id, "time": invoice_time}],
            "invoice_id": invoice_id,
            "invoice_time": invoice_time,
            "processed_timestamp": time.time()
        }
    )
# ==============================================================================
#  ADDITIONAL API ENDPOINTS FOR JAVA INTEGRATION
# ==============================================================================

@app.route("/health", methods=['GET'])
@handle_api_errors
def health_check():
    """Health check endpoint for Java to monitor API status"""
    global command_queue
    
    return api_response(
        success=True,
        message="API is healthy and operational",
        data={
            "status": "healthy",
            "queue_size": len(command_queue),
            "pending_commands": sum(1 for cmd in command_queue.values() if cmd["status"] == "pending"),
            "uptime_seconds": time.time() - app.start_time if hasattr(app, 'start_time') else 0,
            "api_version": "2.0"
        }
    )

@app.route("/api/info", methods=['GET'])
@handle_api_errors
def api_info():
    """API documentation endpoint for Java developers"""
    endpoints = {
        "GET /health": "Health check and status",
        "GET /get_command": "Retrieve pending commands for processing",
        "POST /clear_command": "Clear/acknowledge processed commands",
        "GET /queue_status": "Get detailed queue status",
        "POST /send_command": "Submit new command for processing",
        "GET|POST /task_complete": "Mark task as completed",
        "POST /confirm_invoice": "Confirm invoice processing",
        "GET /api/info": "This endpoint - API documentation",
        "GET /api/stats": "Get API usage statistics"
    }
    
    return api_response(
        success=True,
        message="API information retrieved",
        data={
            "api_name": "LTR Converter Betting API",
            "version": "2.0",
            "endpoints": endpoints,
            "response_format": {
                "success": "boolean - operation success status",
                "message": "string - human readable message",
                "timestamp": "float - unix timestamp",
                "data": "object - response data"
            }
        }
    )

@app.route("/api/stats", methods=['GET'])
@handle_api_errors
def api_stats():
    """API statistics endpoint for monitoring"""
    global command_queue
    
    # Calculate statistics
    total_commands = len(command_queue)
    pending_commands = sum(1 for cmd in command_queue.values() if cmd["status"] == "pending")
    completed_commands = sum(1 for cmd in command_queue.values() if cmd["status"] == "completed")
    
    # Command type breakdown
    command_types = {}
    for cmd_data in command_queue.values():
        cmd_type = cmd_data["command"].get("type", "betting")
        command_types[cmd_type] = command_types.get(cmd_type, 0) + 1
    
    # Age statistics
    current_time = time.time()
    ages = [current_time - cmd_data["timestamp"] for cmd_data in command_queue.values()]
    
    return api_response(
        success=True,
        message="API statistics retrieved",
        data={
            "queue_statistics": {
                "total_commands": total_commands,
                "pending_commands": pending_commands,
                "completed_commands": completed_commands,
                "command_types": command_types
            },
            "timing_statistics": {
                "average_command_age": sum(ages) / len(ages) if ages else 0,
                "oldest_command_age": max(ages) if ages else 0,
                "newest_command_age": min(ages) if ages else 0
            },
            "system_info": {
                "current_timestamp": current_time,
                "incomplete_bets_count": len(INCOMPLETE_BETS_LIST)
            }
        }
    )

if __name__ == '__main__':
    # Set start time for uptime calculation
    app.start_time = time.time()
    print("🚀 Enhanced LTR Converter API starting...")
    print("📚 API Documentation available at: http://localhost:5001/api/info")
    print("❤️ Health check available at: http://localhost:5001/health")
    app.run(host='0.0.0.0', port=5001, debug=True)