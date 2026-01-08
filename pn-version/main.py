from dotenv import load_dotenv
from utils.code_extraction import save_code, extract_markers
from core.prompts import BASE_PROMPT
from core.gen import Gen
from utils.syntax_check import syntax_check
from utils.log import logger

load_dotenv()


def log_feedback(feedback_dict: dict[str, str], round_num: int):
    logger.info(f"[DISCRIMINATOR] Feedback round {round_num}")
    for fname, fb in feedback_dict.items():
        logger.info(f"\nFile: {fname}\nFeedback:\n{fb}\n{'-'*40}")


def main():
    gen = Gen()
    attacks = gen.get_attack_list()

    for attack in attacks:
        logger.info(f"\n[GENERATOR] Initial generation for {attack}")

        syntax_ok = False
        current_feedback = ""
        round_num = 1

        while not syntax_ok:
            prompt = BASE_PROMPT.replace("{attack}", attack).replace("{feedback}", current_feedback)
            reply = gen.ask(prompt)

            code_str = "\n".join(extract_markers(reply))
            syntax_ok, syntax_msg = syntax_check(code_str)

            if syntax_ok:
                save_code(attack, reply, out_dir="scripts")
                logger.info(f"[INFO] After round {round_num} saved {attack} — syntax OK.")
                break
            else:
                logger.warning(f"[DEBUG] After round {round_num} syntax error: {syntax_msg}")
                current_feedback = syntax_msg

            round_num += 1


if __name__ == "__main__":
    main()
