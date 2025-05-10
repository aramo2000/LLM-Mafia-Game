from win_rates import calculate_win_rates_same, calculate_win_rates_different
from deception_detection import llms_deception_detection
from sentiment_readability import sentiment_analysis_dict, compact_sent_analysis_results
from sentiment_readability import readability_analysis_dict, compact_readability_analysis_results


# # generates win rate data for different llm types
# folder_name_different = "generated_data_different"
# json_name = "win_rates_different.json"
# calculate_win_rates_different(folder_name_different, json_name)

# # generates win rate data for same llm types
# folder_name_same = "generated_data_same"
# json_name = "win_rates_same.json"
# calculate_win_rates_same(folder_name_same, json_name)


# # generates deception and detection rates for different llm types
# folder_name = "generated_data_different"
# output_file = "deception_detection_different.json"
# llms_deception_detection(folder_name, output_file)

# # generates deception and detection rates for same llm types
# folder_name = "generated_data_same"
# output_file = "deception_detection_same.json"
# llms_deception_detection(folder_name, output_file)


# # generates sentiment analysis results for different llm types
# folder_name = "generated_data_different"
# output_file = "sentiment_analysis_different.json"
# sent_analysis_dict = sentiment_analysis_dict(folder_name, output_file)
# output_file = "compact_sentiment_analysis_different.json"
# compact_sent_analysis_results(sent_analysis_dict, output_file)

# # generates sentiment analysis results for same llm types
# folder_name = "generated_data_same"
# output_file = "sentiment_analysis_same.json"
# sent_analysis_dict = sentiment_analysis_dict(folder_name, output_file)
# output_file = "compact_sentiment_analysis_same.json"
# compact_sent_analysis_results(sent_analysis_dict, output_file)


# # generates readability analysis results for different llm types
# folder_name = "generated_data_different"
# output_file = "readability_analysis_different.json"
# readability_analysis_dic = readability_analysis_dict(folder_name, output_file)
# output_file = "compact_readability_analysis_different.json"
# compact_readability_analysis_results(readability_analysis_dic, output_file)

# generates readability analysis results for different llm types
folder_name = "generated_data_same"
output_file = "readability_analysis_same.json"
readability_analysis_dic = readability_analysis_dict(folder_name, output_file)
output_file = "compact_readability_analysis_same.json"
compact_readability_analysis_results(readability_analysis_dic, output_file)
